import SwiftUI
import UniformTypeIdentifiers

struct AssetDocumentPicker: UIViewControllerRepresentable {
    @Environment(\.presentationMode) private var presentationMode
    let onPick: (ImportedBundleAsset) -> Void

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let types: [UTType] = [.png, .jpeg, .image, .pdf]
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: types, asCopy: true)
        picker.delegate = context.coordinator
        picker.allowsMultipleSelection = false
        return picker
    }

    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        var parent: AssetDocumentPicker

        init(_ parent: AssetDocumentPicker) {
            self.parent = parent
        }

        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }

            _ = url.startAccessingSecurityScopedResource()
            defer { url.stopAccessingSecurityScopedResource() }

            if let data = try? Data(contentsOf: url) {
                parent.onPick(ImportedBundleAsset(data: data, fileName: url.lastPathComponent))
            }

            parent.presentationMode.wrappedValue.dismiss()
        }

        func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}
