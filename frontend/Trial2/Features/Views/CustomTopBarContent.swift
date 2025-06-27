import SwiftUI

struct CustomTopBarContent: View {
    let title: String
    var showBackButton: Bool = false
    var leadingIcon: String? = nil // Optional custom leading icon
    var trailingIcon: String? = nil // Optional custom trailing icon
    var leadingAction: (() -> Void)? = nil
    var trailingAction: (() -> Void)? = nil

    @Environment(\.dismiss) private var dismiss // For default back button action

    var body: some View {
        HStack {
            // Leading Content (Back Button or Custom Icon)
            if showBackButton {
                Button(action: {
                    leadingAction?() ?? dismiss() // Use custom action or default dismiss
                }) {
                    Image(systemName: "arrow.backward")
                        .font(.title2)
                        .foregroundColor(.primary) // Or your app's accent color
                }
            } else if let leadingIcon = leadingIcon {
                Button(action: {
                    leadingAction?() // Use custom action
                }) {
                    Image(systemName: leadingIcon)
                        .font(.title2)
                        .foregroundColor(.primary)
                }
            } else {
                // Placeholder to align title if no leading button/icon
                Rectangle()
                    .fill(Color.clear)
                    .frame(width: 30) // Match size of an icon/button
            }

            Spacer()

            // Title
            Text(title)
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(.primary)

            Spacer()

            // Trailing Content (Custom Icon)
            if let trailingIcon = trailingIcon {
                Button(action: {
                    trailingAction?() // Use custom action
                }) {
                    Image(systemName: trailingIcon)
                        .font(.title2)
                        .foregroundColor(.primary)
                }
            } else {
                // Placeholder to align title if no trailing button/icon
                Rectangle()
                    .fill(Color.clear)
                    .frame(width: 30) // Match size of an icon/button
            }
        }
        .padding(.horizontal)
        // Note: The .background() and .shadow() will typically be handled by the NavigationView/Toolbar system
        // or by the parent view, as toolbars have their own styling.
    }
}

// MARK: - Preview
#Preview {
    NavigationView { // Embed in NavigationView for preview context
        Color.white.edgesIgnoringSafeArea(.all) // Background for preview
            .toolbar {
                // Example usage in a preview context
                CustomTopBarContent(title: "My Screen", showBackButton: true, trailingIcon: "gearshape.fill") {
                    print("Back tapped in preview")
                } trailingAction: {
                    print("Settings tapped in preview")
                }
            }
            .navigationBarTitleDisplayMode(.inline)
    }
}
