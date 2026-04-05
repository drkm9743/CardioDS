import SwiftUI

// MARK: - Data Model

struct CommunityCard: Identifiable, Codable {
    let id: String
    let name: String
    let issuer: String
    let country: String
    let category: String
    let imageURL: String
    let author: String?
}

struct CommunityCategory: Identifiable {
    let id: String
    let name: String
    let cards: [CommunityCard]
}

struct CommunityCountrySection: Identifiable {
    let id: String
    let name: String
    let flag: String
    let categories: [CommunityCategory]
}

// MARK: - Built-in Catalog

private let builtInCards: [CommunityCard] = [
    // ── United States ── American Express ──
    CommunityCard(id: "amex-gold", name: "Gold Card (Rose Gold)", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexrosegold.png", author: nil),
    CommunityCard(id: "amex-platinum", name: "Platinum Card", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexplat.png", author: nil),
    CommunityCard(id: "amex-biz-gold", name: "Business Gold", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/cubelin/AMEXBizGold.png", author: nil),
    CommunityCard(id: "amex-biz-plat", name: "Business Platinum", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexbizplat.png", author: nil),
    CommunityCard(id: "amex-blue-biz-plus", name: "Blue Business Plus", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexbluebizplus.png", author: nil),
    CommunityCard(id: "amex-biz-green", name: "Business Green", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexbusinessgreen.png", author: nil),
    CommunityCard(id: "amex-amazon-biz", name: "Amazon Business Prime", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexamazonbusinesspr.png", author: nil),
    CommunityCard(id: "amex-green", name: "Green Card", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexgreen.png", author: nil),
    CommunityCard(id: "amex-everyday", name: "EveryDay", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexeveryday.png", author: nil),
    CommunityCard(id: "amex-blue-cash", name: "Blue Cash", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexbluecash.png", author: nil),
    CommunityCard(id: "amex-hilton", name: "Hilton Honors", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexhiltonhonors.png", author: nil),
    CommunityCard(id: "amex-hilton-surpass", name: "Hilton Surpass", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexhiltonsurpass.png", author: nil),
    CommunityCard(id: "amex-marriott-bonvoy", name: "Marriott Bonvoy", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexmarriottbonvoy.png", author: nil),
    CommunityCard(id: "amex-marriott-bonvoy-brill", name: "Marriott Bonvoy Brilliant", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexmarriottbonvoybr.png", author: nil),
    CommunityCard(id: "amex-delta-blue", name: "Delta SkyMiles Blue", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexdeltaskymilesblu.png", author: nil),
    CommunityCard(id: "amex-delta-plat", name: "Delta SkyMiles Platinum", issuer: "American Express", country: "US", category: "Amex", imageURL: "https://u.cubeupload.com/ccbackground/amexdeltaskymilespla.png", author: nil),

    // ── United States ── Chase ──
    CommunityCard(id: "chase-sapphire-pref", name: "Sapphire Preferred", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chasesapphirepreferr.png", author: nil),
    CommunityCard(id: "chase-sapphire-res", name: "Sapphire Reserve", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chasesapphirereserve.png", author: nil),
    CommunityCard(id: "chase-freedom", name: "Freedom", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chasefreedom.png", author: nil),
    CommunityCard(id: "chase-freedom-flex", name: "Freedom Flex", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chasefreedomflex.png", author: nil),
    CommunityCard(id: "chase-freedom-unlimited", name: "Freedom Unlimited", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chasefreedomunlimite.png", author: nil),
    CommunityCard(id: "chase-amazon", name: "Amazon Prime Visa", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chaseamazonprime.png", author: nil),
    CommunityCard(id: "chase-united-exp", name: "United Explorer", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chaseunitedexplorer.png", author: nil),
    CommunityCard(id: "chase-ink-pref", name: "Ink Business Preferred", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chaseinkpreferred.png", author: nil),
    CommunityCard(id: "chase-ink-cash", name: "Ink Business Cash", issuer: "Chase", country: "US", category: "Chase", imageURL: "https://u.cubeupload.com/ccbackground/chaseinkcash.png", author: nil),

    // ── United States ── Capital One ──
    CommunityCard(id: "cap1-quicksilver", name: "Quicksilver", issuer: "Capital One", country: "US", category: "Capital One", imageURL: "https://u.cubeupload.com/ccbackground/quicksilver.png", author: nil),

    // ── United States ── Citi ──
    CommunityCard(id: "citi-double-cash", name: "Double Cash", issuer: "Citi", country: "US", category: "Citi", imageURL: "https://u.cubeupload.com/ccbackground/citidoublecash.png", author: nil),
    CommunityCard(id: "citi-premier", name: "Premier", issuer: "Citi", country: "US", category: "Citi", imageURL: "https://u.cubeupload.com/ccbackground/citipremier.png", author: nil),

    // ── United States ── Other ──
    CommunityCard(id: "apple-card", name: "Apple Card", issuer: "Apple", country: "US", category: "Other US", imageURL: "https://u.cubeupload.com/ccbackground/applecard.png", author: nil),
]

// MARK: - View Model

@MainActor
final class CommunityViewModel: ObservableObject {
    @Published var cards: [CommunityCard] = builtInCards
    @Published var countrySections: [CommunityCountrySection] = []
    @Published var searchText = ""
    @Published var downloadingIDs: Set<String> = []
    @Published var downloadedMessage: String?

    private let countryOrder: [(code: String, name: String, flag: String)] = [
        ("US", "United States", "🇺🇸"),
        ("CA", "Canada", "🇨🇦"),
        ("UK", "United Kingdom", "🇬🇧"),
        ("JP", "Japan", "🇯🇵"),
        ("CN", "China", "🇨🇳"),
        ("KR", "South Korea", "🇰🇷"),
        ("AU", "Australia", "🇦🇺"),
        ("HK", "Hong Kong", "🇭🇰"),
        ("SG", "Singapore", "🇸🇬"),
        ("TW", "Taiwan", "🇹🇼"),
    ]

    private let categoryOrder = ["Amex", "Chase", "Capital One", "Citi", "Other US"]

    init() {
        rebuildSections()
    }

    var filteredSections: [CommunityCountrySection] {
        if searchText.isEmpty { return countrySections }
        let q = searchText.lowercased()
        return countrySections.compactMap { section in
            let filteredCats = section.categories.compactMap { cat in
                let filtered = cat.cards.filter {
                    $0.name.lowercased().contains(q) ||
                    $0.issuer.lowercased().contains(q) ||
                    $0.category.lowercased().contains(q)
                }
                return filtered.isEmpty ? nil : CommunityCategory(id: cat.id, name: cat.name, cards: filtered)
            }
            return filteredCats.isEmpty ? nil : CommunityCountrySection(id: section.id, name: section.name, flag: section.flag, categories: filteredCats)
        }
    }

    private func rebuildSections() {
        // Group cards by country
        var byCountry: [String: [CommunityCard]] = [:]
        for card in cards {
            byCountry[card.country, default: []].append(card)
        }

        var sections: [CommunityCountrySection] = []

        for entry in countryOrder {
            guard let countryCards = byCountry.removeValue(forKey: entry.code), !countryCards.isEmpty else { continue }
            let cats = buildCategories(from: countryCards)
            sections.append(CommunityCountrySection(id: entry.code, name: entry.name, flag: entry.flag, categories: cats))
        }

        // Any remaining countries not in the order
        for (code, countryCards) in byCountry.sorted(by: { $0.key < $1.key }) {
            let cats = buildCategories(from: countryCards)
            sections.append(CommunityCountrySection(id: code, name: code, flag: "🌐", categories: cats))
        }

        countrySections = sections
    }

    private func buildCategories(from cards: [CommunityCard]) -> [CommunityCategory] {
        var dict: [String: [CommunityCard]] = [:]
        for card in cards {
            dict[card.category, default: []].append(card)
        }
        var cats: [CommunityCategory] = []
        for key in categoryOrder {
            if let list = dict.removeValue(forKey: key) {
                cats.append(CommunityCategory(id: key, name: key, cards: list))
            }
        }
        for (key, list) in dict.sorted(by: { $0.key < $1.key }) {
            cats.append(CommunityCategory(id: key, name: key, cards: list))
        }
        return cats
    }

    func downloadCard(_ card: CommunityCard) {
        guard !downloadingIDs.contains(card.id) else { return }
        downloadingIDs.insert(card.id)

        guard let url = URL(string: card.imageURL) else {
            downloadingIDs.remove(card.id)
            return
        }

        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.downloadingIDs.remove(card.id)
                guard let data = data, error == nil,
                      let httpResp = response as? HTTPURLResponse,
                      httpResp.statusCode == 200 else {
                    self?.downloadedMessage = "Download failed: \(error?.localizedDescription ?? "unknown error")"
                    return
                }

                // Save to Documents
                let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
                let safeName = "\(card.issuer)_\(card.name)"
                    .replacingOccurrences(of: " ", with: "_")
                    .replacingOccurrences(of: "/", with: "_")

                let ext = card.imageURL.lowercased().hasSuffix(".png") ? "png" : "png"
                let dest = docs.appendingPathComponent("\(safeName).\(ext)")

                do {
                    // Convert to PNG if needed
                    if let image = UIImage(data: data), let pngData = image.pngData() {
                        try pngData.write(to: dest, options: .atomic)
                    } else {
                        try data.write(to: dest, options: .atomic)
                    }
                    self?.downloadedMessage = "\(card.name) saved to Documents"
                } catch {
                    self?.downloadedMessage = "Save failed: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

// MARK: - Community View

struct CommunityView: View {
    @StateObject private var vm = CommunityViewModel()
    @State private var showAlert = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Community Cards")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)

                    Text("Download card backgrounds and apply them from your photo library.")
                        .font(.system(size: 13))
                        .foregroundColor(.white.opacity(0.6))
                        .padding(.horizontal, 16)

                    // Search
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.gray)
                        TextField("Search cards...", text: $vm.searchText)
                            .foregroundColor(.white)
                    }
                    .padding(10)
                    .background(Color.white.opacity(0.1))
                    .cornerRadius(10)
                    .padding(.horizontal, 16)

                    // Card grid by country → category
                    ForEach(vm.filteredSections) { section in
                        VStack(alignment: .leading, spacing: 12) {
                            Text("\(section.flag) \(section.name)")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                                .padding(.horizontal, 16)

                            ForEach(section.categories) { category in
                                VStack(alignment: .leading, spacing: 8) {
                                    Text(category.name)
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(.white.opacity(0.85))
                                        .padding(.horizontal, 16)

                                    ScrollView(.horizontal, showsIndicators: false) {
                                        HStack(spacing: 12) {
                                            ForEach(category.cards) { card in
                                                CommunityCardCell(card: card, vm: vm)
                                            }
                                        }
                                        .padding(.horizontal, 16)
                                    }
                                }
                            }
                        }
                        .padding(.bottom, 8)
                    }

                    // Attribution
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Card images from the community at")
                            .font(.system(size: 11))
                            .foregroundColor(.white.opacity(0.4))
                        Link("dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh",
                             destination: URL(string: "https://dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh")!)
                        .font(.system(size: 11))
                        .foregroundColor(.cyan.opacity(0.6))
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                    .padding(.bottom, 20)
                }
                .padding(.top, 12)
            }
        }
        .onChange(of: vm.downloadedMessage) { msg in
            if msg != nil { showAlert = true }
        }
        .alert("Download", isPresented: $showAlert) {
            Button("OK") { vm.downloadedMessage = nil }
        } message: {
            Text(vm.downloadedMessage ?? "")
        }
    }
}

// MARK: - Image Loader (replaces AsyncImage for reliability)

@MainActor
final class RemoteImageLoader: ObservableObject {
    @Published var image: UIImage?
    @Published var failed = false
    @Published var loading = false

    private var url: URL?
    private var retryCount = 0
    private static let maxRetries = 2

    func load(from urlString: String) {
        guard let url = URL(string: urlString) else {
            failed = true
            return
        }
        self.url = url
        retryCount = 0
        fetchImage()
    }

    func retry() {
        failed = false
        retryCount = 0
        fetchImage()
    }

    private func fetchImage() {
        guard let url else { return }
        loading = true

        var request = URLRequest(url: url)
        request.timeoutInterval = 15
        request.cachePolicy = .returnCacheDataElseLoad

        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                guard let self else { return }
                self.loading = false

                if let data, error == nil,
                   let httpResp = response as? HTTPURLResponse,
                   httpResp.statusCode == 200,
                   let img = UIImage(data: data) {
                    self.image = img
                } else if self.retryCount < Self.maxRetries {
                    self.retryCount += 1
                    DispatchQueue.main.asyncAfter(deadline: .now() + Double(self.retryCount) * 0.5) {
                        self.fetchImage()
                    }
                } else {
                    self.failed = true
                }
            }
        }.resume()
    }
}

// MARK: - Card Cell

struct CommunityCardCell: View {
    let card: CommunityCard
    @ObservedObject var vm: CommunityViewModel
    @StateObject private var loader = RemoteImageLoader()

    var body: some View {
        VStack(spacing: 6) {
            Group {
                if let image = loader.image {
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 200, height: 126)
                        .clipped()
                        .cornerRadius(10)
                } else if loader.failed {
                    placeholder
                        .overlay(
                            VStack(spacing: 4) {
                                Image(systemName: "arrow.clockwise")
                                    .foregroundColor(.orange)
                                Text("Tap to retry")
                                    .font(.system(size: 9))
                                    .foregroundColor(.orange)
                            }
                        )
                        .onTapGesture {
                            loader.retry()
                        }
                } else {
                    placeholder
                        .overlay(ProgressView().tint(.white))
                }
            }
            .frame(width: 200, height: 126)
            .onAppear {
                if loader.image == nil && !loader.loading {
                    loader.load(from: card.imageURL)
                }
            }

            Text(card.name)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white)
                .lineLimit(1)
                .frame(width: 200)

            Text(card.issuer)
                .font(.system(size: 10))
                .foregroundColor(.white.opacity(0.5))

            Button {
                vm.downloadCard(card)
            } label: {
                if vm.downloadingIDs.contains(card.id) {
                    ProgressView()
                        .tint(.white)
                        .frame(height: 28)
                } else {
                    Label("Save", systemImage: "square.and.arrow.down")
                        .font(.system(size: 12, weight: .medium))
                        .frame(height: 28)
                }
            }
            .frame(width: 180, height: 32)
            .background(Color.white.opacity(0.15))
            .cornerRadius(8)
            .foregroundColor(.cyan)
        }
        .padding(.vertical, 4)
    }

    private var placeholder: some View {
        RoundedRectangle(cornerRadius: 10)
            .fill(Color.white.opacity(0.08))
            .frame(width: 200, height: 126)
    }
}
