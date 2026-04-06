import SwiftUI
import UniformTypeIdentifiers

struct DocumentPicker: UIViewControllerRepresentable {
    @Environment(\.presentationMode) private var presentationMode
    @Binding var selectedImage: UIImage

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let types: [UTType] = [.png, .jpeg, .image]
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
        var parent: DocumentPicker

        init(_ parent: DocumentPicker) {
            self.parent = parent
        }

        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }

            _ = url.startAccessingSecurityScopedResource()
            defer { url.stopAccessingSecurityScopedResource() }

            if let data = try? Data(contentsOf: url),
               let image = UIImage(data: data) {
                parent.selectedImage = image
            }

            parent.presentationMode.wrappedValue.dismiss()
        }

        func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}
