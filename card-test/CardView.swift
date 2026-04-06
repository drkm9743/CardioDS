import SwiftUI
import PDFKit

struct Card: Identifiable {
    var imagePath: String
    var directoryPath: String
    var bundleName: String
    var backgroundFileName: String

    var id: String {
        directoryPath
    }

    var displayName: String {
        CardNicknameManager.shared.nickname(for: directoryPath) ?? bundleName
    }
}

// MARK: - Nickname Manager

final class CardNicknameManager {
    static let shared = CardNicknameManager()
    private let key = "cardio.card.nicknames"

    private var cache: [String: String]

    private init() {
        cache = (UserDefaults.standard.dictionary(forKey: key) as? [String: String]) ?? [:]
    }

    func nickname(for directoryPath: String) -> String? {
        cache[directoryPath]
    }

    func setNickname(_ name: String?, for directoryPath: String) {
        if let name, !name.trimmingCharacters(in: .whitespaces).isEmpty {
            cache[directoryPath] = name.trimmingCharacters(in: .whitespaces)
        } else {
            cache.removeValue(forKey: directoryPath)
        }
        UserDefaults.standard.set(cache, forKey: key)
    }
}

private let helper = ObjcHelper()

struct CardView: View {
    let fm = FileManager.default
    let card: Card
    @ObservedObject var exploit: ExploitManager

    @State private var cardImage = UIImage()
    @State private var showSheet = false
    @State private var showDocPicker = false
    @State private var showSourcePicker = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var imageVersion = 0          // bump to force re-render
    @State private var showSaved = false
    @State private var showNicknameEditor = false
    @State private var nicknameInput = ""
    @State private var showCardNumberEditor = false
    @State private var cardNumberInput = ""
    @State private var currentCardNumber = ""

    private var cardDirectoryPath: String {
        return card.directoryPath
    }

    private var targetPath: String {
        return cardDirectoryPath + "/" + card.backgroundFileName
    }

    private var backupPath: String {
        return targetPath + ".backup"
    }

    private var cachePath: String {
        if cardDirectoryPath.lowercased().hasSuffix(".pkpass") {
            return cardDirectoryPath.replacingOccurrences(of: "pkpass", with: "cache")
        }
        return cardDirectoryPath + ".cache"
    }

    private func removeCacheIfPresent() {
        if fm.fileExists(atPath: cachePath) {
            try? fm.removeItem(atPath: cachePath)
        }
    }

    private func backupCurrentIfNeeded() throws {
        guard exploit.directWriteReady else {
            return
        }

        if fm.fileExists(atPath: targetPath) && !fm.fileExists(atPath: backupPath) {
            try fm.moveItem(atPath: targetPath, toPath: backupPath)
        }
    }

    private func previewImage() -> UIImage? {
        let lower = card.backgroundFileName.lowercased()

        // Try direct filesystem access first
        if lower.hasSuffix(".pdf") {
            if let doc = PDFDocument(url: URL(fileURLWithPath: card.imagePath)),
               let page = doc.page(at: 0) {
                return page.thumbnail(of: CGSize(width: 640, height: 400), for: .cropBox)
            }
        } else {
            if let img = UIImage(contentsOfFile: card.imagePath) {
                return img
            }
        }

        // Direct access failed (sandbox) — try reading via kernel read
        if let data = helper.kfsReadFile(card.imagePath, maxSize: 8 * 1024 * 1024) {
            if lower.hasSuffix(".pdf") {
                if let doc = PDFDocument(data: data),
                   let page = doc.page(at: 0) {
                    return page.thumbnail(of: CGSize(width: 640, height: 400), for: .cropBox)
                }
            } else {
                return UIImage(data: data)
            }
        }

        // Can't read image data — return nil (UI will show placeholder)
        return nil
    }

    private func guardWriteAccessOrShowError() -> Bool {
        if exploit.canApplyCardChanges {
            return true
        }

        errorMessage = exploit.blockedReason
        showError = true
        return false
    }

    // MARK: - pass.json card number editing

    private var passJsonPath: String {
        cardDirectoryPath + "/pass.json"
    }

    private var passJsonBackupPath: String {
        cardDirectoryPath + "/pass.json.backup"
    }

    private func readPassJson() -> Data? {
        if let data = fm.contents(atPath: passJsonPath) {
            return data
        }
        return helper.kfsReadFile(passJsonPath, maxSize: 512 * 1024)
    }

    private func readCardNumber() -> String? {
        guard let data = readPassJson(),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let suffix = json["primaryAccountSuffix"] as? String else {
            return nil
        }
        return suffix
    }

    private func backupPassJsonIfNeeded() throws {
        guard exploit.directWriteReady || exploit.canApplyCardChanges else { return }
        if fm.fileExists(atPath: passJsonPath) && !fm.fileExists(atPath: passJsonBackupPath) {
            if exploit.directWriteReady {
                try fm.copyItem(atPath: passJsonPath, toPath: passJsonBackupPath)
            } else if let data = readPassJson() {
                try exploit.overwriteWalletFile(targetPath: passJsonBackupPath, data: data)
            }
        }
    }

    private func applyCardNumber(_ newSuffix: String) {
        if !guardWriteAccessOrShowError() { return }

        guard let data = readPassJson(),
              var json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            errorMessage = NSLocalizedString("card_number_read_error", comment: "")
            showError = true
            return
        }

        do {
            try backupPassJsonIfNeeded()

            let trimmed = newSuffix.trimmingCharacters(in: .whitespaces)
            if trimmed.isEmpty {
                json.removeValue(forKey: "primaryAccountSuffix")
            } else {
                json["primaryAccountSuffix"] = trimmed
            }

            let newData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try exploit.overwriteWalletFile(targetPath: passJsonPath, data: newData)
            removeCacheIfPresent()
            currentCardNumber = trimmed
            helper.refreshWalletServices()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    private func restorePassJson() {
        if !guardWriteAccessOrShowError() { return }

        guard fm.fileExists(atPath: passJsonBackupPath) || readPassJson() != nil else {
            errorMessage = NSLocalizedString("card_number_no_backup", comment: "")
            showError = true
            return
        }

        do {
            if exploit.directWriteReady && fm.fileExists(atPath: passJsonBackupPath) {
                if fm.fileExists(atPath: passJsonPath) {
                    try fm.removeItem(atPath: passJsonPath)
                }
                try fm.copyItem(atPath: passJsonBackupPath, toPath: passJsonPath)
            } else {
                try exploit.overwriteWalletFile(targetPath: passJsonPath, sourcePath: passJsonBackupPath)
            }
            removeCacheIfPresent()
            currentCardNumber = readCardNumber() ?? ""
            helper.refreshWalletServices()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    private func applyReplacementData(_ data: Data) {
        if !guardWriteAccessOrShowError() {
            return
        }

        do {
            try backupCurrentIfNeeded()
            try exploit.overwriteWalletFile(targetPath: targetPath, data: data)
            removeCacheIfPresent()
            imageVersion += 1
            helper.refreshWalletServices()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    private func resetImage() {
        if !guardWriteAccessOrShowError() {
            return
        }

        guard fm.fileExists(atPath: backupPath) else {
            errorMessage = "No backup found for this card"
            showError = true
            return
        }

        do {
            if exploit.directWriteReady {
                if fm.fileExists(atPath: targetPath) {
                    try fm.removeItem(atPath: targetPath)
                }
                try fm.moveItem(atPath: backupPath, toPath: targetPath)
            } else {
                try exploit.overwriteWalletFile(targetPath: targetPath, sourcePath: backupPath)
            }

            removeCacheIfPresent()
            imageVersion += 1
            helper.refreshWalletServices()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    private func saveToDocuments() {
        guard let image = previewImage() else {
            errorMessage = "Cannot read card image"
            showError = true
            return
        }

        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let safeName = card.bundleName
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: " ", with: "_")
        let dest = docs.appendingPathComponent("\(safeName).png")

        do {
            if let data = image.pngData() {
                try data.write(to: dest, options: .atomic)
                showSaved = true
            } else {
                errorMessage = "Could not encode image"
                showError = true
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    private func setImage(image: UIImage) {
        let lower = card.backgroundFileName.lowercased()

        if lower.hasSuffix(".png") {
            guard let data = image.pngData() else {
                errorMessage = "Could not encode PNG"
                showError = true
                return
            }
            applyReplacementData(data)

        } else if lower.hasSuffix(".pdf") {
            let pdfDocument = PDFDocument()
            guard let page = PDFPage(image: image) else {
                errorMessage = "Unable to create PDF page"
                showError = true
                return
            }
            pdfDocument.insert(page, at: 0)

            guard let data = pdfDocument.dataRepresentation() else {
                errorMessage = "Unable to encode PDF"
                showError = true
                return
            }
            applyReplacementData(data)

        } else {
            errorMessage = "Unknown format"
            showError = true
        }
    }

    var body: some View {
        VStack(spacing: 8) {
            // Card image (tappable to replace)
            Group {
                if let preview = previewImage() {
                    Image(uiImage: preview)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 320)
                        .cornerRadius(10)
                } else {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(
                            LinearGradient(
                                colors: [Color.blue.opacity(0.4), Color.purple.opacity(0.3)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 320, height: 200)
                        .overlay(
                            VStack(spacing: 8) {
                                Image(systemName: "creditcard.fill")
                                    .font(.system(size: 36))
                                    .foregroundColor(.white.opacity(0.8))
                                Text(card.bundleName)
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.white)
                                    .lineLimit(2)
                                    .multilineTextAlignment(.center)
                            }
                            .padding()
                        )
                }
            }
            .id(imageVersion)   // force re-render when bumped
            .onTapGesture {
                if exploit.canApplyCardChanges {
                    showSourcePicker = true
                } else {
                    errorMessage = exploit.blockedReason
                    showError = true
                }
            }
            .confirmationDialog("card_pick_source", isPresented: $showSourcePicker, titleVisibility: .visible) {
                Button("card_source_gallery") { showSheet = true }
                Button("card_source_files") { showDocPicker = true }
                Button("card_cancel", role: .cancel) {}
            }
            .sheet(isPresented: $showSheet) {
                ImagePicker(sourceType: .photoLibrary, selectedImage: self.$cardImage)
            }
            .sheet(isPresented: $showDocPicker) {
                DocumentPicker(selectedImage: self.$cardImage)
            }
            .onChange(of: self.cardImage) { newImage in
                setImage(image: newImage)
            }

            Text(card.displayName)
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.8))
                .lineLimit(1)

            if card.displayName != card.bundleName {
                Text(card.bundleName)
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.white.opacity(0.35))
                    .lineLimit(1)
            }

            // Action buttons
            HStack(spacing: 16) {
                Button {
                    nicknameInput = CardNicknameManager.shared.nickname(for: card.directoryPath) ?? ""
                    showNicknameEditor = true
                } label: {
                    Label("card_rename", systemImage: "pencil")
                        .font(.system(size: 13))
                }
                .foregroundColor(.white.opacity(0.7))

                Button {
                    currentCardNumber = readCardNumber() ?? ""
                    cardNumberInput = currentCardNumber
                    showCardNumberEditor = true
                } label: {
                    Label("card_number_edit", systemImage: "number")
                        .font(.system(size: 13))
                }
                .foregroundColor(.white.opacity(0.7))

                if fm.fileExists(atPath: backupPath) || imageVersion > 0 {
                    Button {
                        resetImage()
                    } label: {
                        Label("card_restore", systemImage: "arrow.counterclockwise")
                            .font(.system(size: 13))
                    }
                    .foregroundColor(.red)
                }

                Button {
                    saveToDocuments()
                } label: {
                    Label("card_save", systemImage: "square.and.arrow.down")
                        .font(.system(size: 13))
                }
                .foregroundColor(.cyan)
            }
            .padding(.top, 4)
        }
        .alert("card_error", isPresented: $showError) {
            Button("card_ok", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
        .alert("card_saved", isPresented: $showSaved) {
            Button("card_ok", role: .cancel) {}
        } message: {
            Text("card_saved_message")
        }
        .alert("card_rename_title", isPresented: $showNicknameEditor) {
            TextField(NSLocalizedString("card_nickname_placeholder", comment: ""), text: $nicknameInput)
            Button("card_rename_save") {
                CardNicknameManager.shared.setNickname(nicknameInput.isEmpty ? nil : nicknameInput, for: card.directoryPath)
            }
            Button("card_clear_name", role: .destructive) {
                CardNicknameManager.shared.setNickname(nil, for: card.directoryPath)
                nicknameInput = ""
            }
            Button("card_cancel", role: .cancel) {}
        } message: {
            Text("card_rename_message")
        }
        .alert("card_number_title", isPresented: $showCardNumberEditor) {
            TextField(NSLocalizedString("card_number_placeholder", comment: ""), text: $cardNumberInput)
            Button("card_rename_save") {
                applyCardNumber(cardNumberInput)
            }
            if fm.fileExists(atPath: passJsonBackupPath) {
                Button("card_number_restore_original", role: .destructive) {
                    restorePassJson()
                }
            }
            Button("card_cancel", role: .cancel) {}
        } message: {
            Text(currentCardNumber.isEmpty
                 ? NSLocalizedString("card_number_message_empty", comment: "")
                 : String(format: NSLocalizedString("card_number_message", comment: ""), currentCardNumber))
        }
    }
}
