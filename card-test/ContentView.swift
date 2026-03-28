import SwiftUI
import UIKit

struct ContentView: View {
    @StateObject private var exploit = ExploitManager.shared
    @State private var showNoCardsError = false
    @State private var cards: [Card] = []
    @State private var detectedCardsRoot = "not-detected"
    @State private var usedKfsForScan = false
    @State private var offsetInput = ""
    @State private var showLogShareSheet = false
    @State private var shareItems: [Any] = []

    private let helper = ObjcHelper()

    private struct CardBundleCandidate {
        let directoryPath: String
        let bundleName: String
        let backgroundFileName: String
    }

    private func joinPath(_ parent: String, _ child: String) -> String {
        if parent.hasSuffix("/") {
            return parent + child
        }
        return parent + "/" + child
    }

    private func scanLog(_ message: String) {
        exploit.addLog("[scan] \(message)")
    }

    private func pathVariants(for path: String) -> [String] {
        var variants: [String] = [path]
        if path.hasPrefix("/private/var/") {
            variants.append(String(path.dropFirst("/private".count)))
        } else if path.hasPrefix("/var/") {
            variants.append("/private" + path)
        }

        var unique: [String] = []
        for variant in variants where !unique.contains(variant) {
            unique.append(variant)
        }
        return unique
    }

    private func listDirectory(_ path: String, usedKfs: inout Bool) -> [String] {
        let fm = FileManager.default

        for variant in pathVariants(for: path) {
            if let direct = try? fm.contentsOfDirectory(atPath: variant) {
                return direct
            }
        }

        guard exploit.kfsReady else {
            return []
        }

        for variant in pathVariants(for: path) {
            let viaKfs = helper.kfsListDirectory(variant)
            if !viaKfs.isEmpty {
                usedKfs = true
                return viaKfs
            }
        }

        return []
    }

    private func cardBackgroundFile(in cardDirectory: String, usedKfs: inout Bool) -> String? {
        let files = listDirectory(cardDirectory, usedKfs: &usedKfs)
        guard !files.isEmpty else {
            return nil
        }

        let preferred = [
            "cardBackgroundCombined@2x.png",
            "cardBackgroundCombined@3x.png",
            "cardBackgroundCombined.png",
            "cardBackgroundCombined.pdf"
        ]

        for name in preferred where files.contains(name) {
            return name
        }

        return files.first { file in
            let lower = file.lowercased()
            return lower.hasPrefix("cardbackgroundcombined") && (lower.hasSuffix(".png") || lower.hasSuffix(".pdf"))
        }
    }

    private func collectCardBundles(in cardsRoot: String, usedKfs: inout Bool) -> [CardBundleCandidate] {
        let entries = listDirectory(cardsRoot, usedKfs: &usedKfs)
        guard !entries.isEmpty else {
            return []
        }

        var bundles: [CardBundleCandidate] = []
        var seenDirectories: Set<String> = []

        for entry in entries {
            if entry == "." || entry == ".." {
                continue
            }

            let candidateDirectory = joinPath(cardsRoot, entry)
            if let backgroundFile = cardBackgroundFile(in: candidateDirectory, usedKfs: &usedKfs) {
                if !seenDirectories.contains(candidateDirectory) {
                    bundles.append(
                        CardBundleCandidate(
                            directoryPath: candidateDirectory,
                            bundleName: entry,
                            backgroundFileName: backgroundFile
                        )
                    )
                    seenDirectories.insert(candidateDirectory)
                }
                continue
            }

            // On some versions, card bundles are nested one level deeper.
            let nestedEntries = listDirectory(candidateDirectory, usedKfs: &usedKfs)
            for nested in nestedEntries {
                if nested == "." || nested == ".." {
                    continue
                }

                let nestedDirectory = joinPath(candidateDirectory, nested)
                if let backgroundFile = cardBackgroundFile(in: nestedDirectory, usedKfs: &usedKfs), !seenDirectories.contains(nestedDirectory) {
                    bundles.append(
                        CardBundleCandidate(
                            directoryPath: nestedDirectory,
                            bundleName: "\(entry)/\(nested)",
                            backgroundFileName: backgroundFile
                        )
                    )
                    seenDirectories.insert(nestedDirectory)
                }
            }
        }

        return bundles
    }

    private func discoverCardsRoot(usedKfs: inout Bool) -> String? {
        var candidates: [String] = []

        if let detected = exploit.detectedCardsRootPath {
            candidates.append(detected)
        }
        for candidate in exploit.knownCardsRootCandidates where !candidates.contains(candidate) {
            candidates.append(candidate)
        }

        for candidate in candidates {
            let found = collectCardBundles(in: candidate, usedKfs: &usedKfs)
            if !found.isEmpty {
                scanLog("candidate \(candidate) yielded \(found.count) card bundle(s)")
                return candidate
            }
        }

        let passContainers = [
            "/var/mobile/Library/Passes",
            "/private/var/mobile/Library/Passes"
        ]

        for container in passContainers {
            let topEntries = listDirectory(container, usedKfs: &usedKfs)

            for primary in ["Cards", "Passes", "Wallet"] where topEntries.contains(primary) {
                let candidate = joinPath(container, primary)
                if !collectCardBundles(in: candidate, usedKfs: &usedKfs).isEmpty {
                    return candidate
                }

                let nestedCards = joinPath(candidate, "Cards")
                if !collectCardBundles(in: nestedCards, usedKfs: &usedKfs).isEmpty {
                    return nestedCards
                }
            }

            for entry in topEntries {
                if entry == "." || entry == ".." {
                    continue
                }

                let lower = entry.lowercased()
                if !(lower.contains("card") || lower.contains("pass") || lower.contains("wallet")) {
                    continue
                }

                let candidate = joinPath(container, entry)
                if !collectCardBundles(in: candidate, usedKfs: &usedKfs).isEmpty {
                    return candidate
                }

                let nestedCards = joinPath(candidate, "Cards")
                if !collectCardBundles(in: nestedCards, usedKfs: &usedKfs).isEmpty {
                    return nestedCards
                }
            }
        }

        scanLog("no card bundles found in known pass containers")
        return nil
    }

    private func buildLogExportText() -> String {
        let timestamp = ISO8601DateFormatter().string(from: Date())
        let header = [
            "CardioSword diagnostic export",
            "timestamp=\(timestamp)",
            "status=\(exploit.statusMessage)",
            "darksword_ready=\(exploit.darkswordReady)",
            "kfs_ready=\(exploit.kfsReady)",
            "kernproc_offset=\(exploit.hasKernprocOffset ? String(format: \"0x%llx\", exploit.kernprocOffset) : \"missing\")",
            "cards_root=\(detectedCardsRoot)",
            "scan_mode=\(usedKfsForScan ? \"kfs\" : \"direct\")",
            ""
        ].joined(separator: "\n")

        let body = exploit.logText.isEmpty ? "No logs yet." : exploit.logText
        return header + body
    }

    private func loadCards() {
        cards = getPasses()
    }

    private func getPasses() -> [Card] {
        var usedKfs = false
        guard let cardsRoot = discoverCardsRoot(usedKfs: &usedKfs) else {
            usedKfsForScan = usedKfs
            detectedCardsRoot = "not-detected"
            exploit.setDetectedCardsRootPath(nil)
            return []
        }

        exploit.setDetectedCardsRootPath(cardsRoot)
        detectedCardsRoot = cardsRoot

        var data = [Card]()

        let bundles = collectCardBundles(in: cardsRoot, usedKfs: &usedKfs)
        scanLog("final scan root=\(cardsRoot) bundles=\(bundles.count)")

        for bundle in bundles {
            data.append(
                Card(
                    imagePath: joinPath(bundle.directoryPath, bundle.backgroundFileName),
                    directoryPath: bundle.directoryPath,
                    bundleName: bundle.bundleName,
                    backgroundFileName: bundle.backgroundFileName
                )
            )
        }

        usedKfsForScan = usedKfs
        return data
    }

    private func refreshOffsetInputFromState() {
        if exploit.hasKernprocOffset {
            offsetInput = String(format: "0x%llx", exploit.kernprocOffset)
        }
    }

    private func recheckAndReload() {
        exploit.refreshAccessProbe()
        exploit.refreshKernprocOffsetState()
        loadCards()
    }

    private func runAllAndReload() {
        exploit.runAll { _ in
            recheckAndReload()
            if cards.isEmpty {
                showNoCardsError = true
            }
        }
    }

    private var exploitPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Exploit Engine")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.white)

            Text(exploit.statusMessage)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(exploit.canApplyCardChanges ? .green : .orange)

            Text(String(
                format: "darksword=%@ | kfs=%@",
                exploit.darkswordReady ? "ready" : "not-ready",
                exploit.kfsReady ? "ready" : "not-ready"
            ))
            .font(.system(size: 12, weight: .regular, design: .monospaced))
            .foregroundColor(.white.opacity(0.85))

            Text(exploit.hasKernprocOffset
                 ? String(format: "kernproc_offset=0x%llx", exploit.kernprocOffset)
                 : "kernproc_offset=missing")
            .font(.system(size: 11, design: .monospaced))
            .foregroundColor(exploit.hasKernprocOffset ? .green.opacity(0.9) : .orange)

            Text("cards_root=\(detectedCardsRoot)")
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))

            Text("scan_mode=\(usedKfsForScan ? "kfs" : "direct")")
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))

            if exploit.darkswordReady {
                Text(String(
                    format: "kernel_base=0x%llx slide=0x%llx",
                    exploit.kernelBase,
                    exploit.kernelSlide
                ))
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))

                Text(String(
                    format: "our_proc=0x%llx our_task=0x%llx",
                    exploit.ourProc,
                    exploit.ourTask
                ))
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))
            }

            HStack(spacing: 8) {
                TextField("kernproc offset (hex)", text: $offsetInput)
                    .textFieldStyle(.roundedBorder)

                Button("Set") {
                    if exploit.setKernprocOffset(from: offsetInput) {
                        refreshOffsetInputFromState()
                        recheckAndReload()
                    }
                }
                .foregroundColor(.white)

                Button("Import lara") {
                    _ = exploit.importLaraKernprocOffset()
                    refreshOffsetInputFromState()
                    recheckAndReload()
                }
                .foregroundColor(.white)
            }

            HStack(spacing: 10) {
                Button(exploit.darkswordRunning ? "Running DarkSword..." : "Run DarkSword") {
                    exploit.runDarksword { _ in
                        recheckAndReload()
                    }
                }
                .disabled(exploit.darkswordRunning || exploit.kfsRunning)
                .foregroundColor(.white)

                Button(exploit.kfsRunning ? "Init KFS..." : "Init KFS") {
                    exploit.initKFS { _ in
                        recheckAndReload()
                    }
                }
                .disabled(exploit.darkswordRunning || exploit.kfsRunning)
                .foregroundColor(.white)

                Button("Run All") {
                    runAllAndReload()
                }
                .disabled(exploit.darkswordRunning || exploit.kfsRunning)
                .foregroundColor(.white)
            }

            HStack(spacing: 10) {
                Button("Copy Logs") {
                    UIPasteboard.general.string = buildLogExportText()
                    scanLog("logs copied to clipboard")
                }
                .foregroundColor(.white)

                Button("Share Logs") {
                    shareItems = [buildLogExportText()]
                    showLogShareSheet = true
                }
                .foregroundColor(.white)
            }

            ScrollView {
                Text(exploit.logText.isEmpty ? "No logs yet." : exploit.logText)
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundColor(Color.green.opacity(0.9))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(8)
            }
            .frame(height: 120)
            .background(Color.white.opacity(0.06))
            .cornerRadius(8)
        }
        .padding(12)
        .background(Color.white.opacity(0.09))
        .cornerRadius(12)
        .padding(.horizontal, 14)
    }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack(spacing: 12) {
                Text("Tap a card to customize")
                    .font(.system(size: 25))
                    .foregroundColor(.white)

                Text("Swipe to view different cards")
                    .font(.system(size: 15))
                    .foregroundColor(.white)

                exploitPanel

                if !cards.isEmpty {
                    TabView {
                        ForEach(cards) { card in
                            CardView(card: card, exploit: exploit)
                        }
                    }
                    .tabViewStyle(PageTabViewStyle(indexDisplayMode: .always))
                    .frame(height: 340)

                    Button("Refresh Cards") {
                        loadCards()
                        if cards.isEmpty {
                            showNoCardsError = true
                        }
                    }
                    .foregroundColor(.white)
                    .padding(.top, 16)
                } else {
                    VStack(spacing: 12) {
                        Text("No Cards Found").foregroundColor(.red)

                        Text("Path: \(detectedCardsRoot)")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white.opacity(0.75))

                        Text(usedKfsForScan ? "Directory scan via KFS" : "Directory scan via direct filesystem")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white.opacity(0.75))

                        Button("Run All + Scan") {
                            runAllAndReload()
                        }
                        .foregroundColor(.white)

                        Button("Scan Again") {
                            loadCards()
                            if cards.isEmpty {
                                showNoCardsError = true
                            }
                        }
                        .foregroundColor(.white)
                    }
                }
            }
            .alert(isPresented: $showNoCardsError) {
                Alert(
                    title: Text("No Cards Were Found"),
                    message: Text("Last detected cards root: \(detectedCardsRoot)")
                )
            }
        }
        .onAppear {
            recheckAndReload()
            refreshOffsetInputFromState()
        }
        .sheet(isPresented: $showLogShareSheet) {
            ShareSheet(activityItems: shareItems)
        }
    }
}

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
