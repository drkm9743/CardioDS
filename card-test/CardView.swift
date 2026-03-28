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
}

private let helper = ObjcHelper()

struct CardView: View {
    let fm = FileManager.default
    let card: Card
    @ObservedObject var exploit: ExploitManager

    @State private var cardImage = UIImage()
    @State private var showSheet = false
    @State private var showError = false
    @State private var errorMessage = ""

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
        if lower.hasSuffix(".pdf") {
            guard let doc = PDFDocument(url: URL(fileURLWithPath: card.imagePath)),
                  let page = doc.page(at: 0) else {
                return nil
            }
            return page.thumbnail(of: CGSize(width: 640, height: 400), for: .cropBox)
        }
        return UIImage(contentsOfFile: card.imagePath)
    }

    private func guardWriteAccessOrShowError() -> Bool {
        if exploit.canApplyCardChanges {
            return true
        }

        errorMessage = exploit.blockedReason
        showError = true
        return false
    }

    private func applyReplacementData(_ data: Data) {
        if !guardWriteAccessOrShowError() {
            return
        }

        do {
            try backupCurrentIfNeeded()
            try exploit.overwriteWalletFile(targetPath: targetPath, data: data)
            removeCacheIfPresent()
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
            helper.refreshWalletServices()
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
        ZStack {
            if let preview = previewImage() {
                Image(uiImage: preview)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 320)
                    .zIndex(0)
                    .cornerRadius(5)
                    .onTapGesture {
                        if exploit.canApplyCardChanges {
                            showSheet = true
                        } else {
                            errorMessage = exploit.blockedReason
                            showError = true
                        }
                    }
                    .sheet(isPresented: $showSheet) {
                        ImagePicker(sourceType: .photoLibrary, selectedImage: self.$cardImage)
                    }
                    .onChange(of: self.cardImage) { newImage in
                        setImage(image: newImage)
                    }
            } else {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.25))
                    .frame(width: 320, height: 200)
                    .overlay(Text("Preview unavailable").foregroundColor(.white))
            }

            if fm.fileExists(atPath: backupPath) {
                Button {
                    resetImage()
                } label: {
                    Image(systemName: "arrow.counterclockwise.circle.fill")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40)
                        .foregroundColor(exploit.canApplyCardChanges ? Color.red : Color.gray)
                }
                .zIndex(1)
                .padding(.top, 265)
            }
        }
        .alert(isPresented: $showError) {
            Alert(
                title: Text("Error Occured"),
                message: Text(errorMessage)
            )
        }
    }
}
