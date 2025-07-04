import SwiftUI

struct CustomTopBarContent: View {
    let title: String
    var showBackButton: Bool = false
    var leadingIcon: String? = nil
    var trailingIcon: String? = nil
    var leadingAction: (() -> Void)? = nil
    var trailingAction: (() -> Void)? = nil

    var body: some View {
        HStack {
            // Leading: Back button or icon
            if showBackButton {
                Button(action: {
                    leadingAction?()
                }) {
                    Image(systemName: "chevron.left")
                        .font(.title3.bold())
                        .foregroundColor(.blue)
                        .padding(10)
                        .background(Color.white.opacity(0.25))
                        .clipShape(Circle())
                        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                }
                .padding(.leading, -4) // ⬅️ shifted more left
            } else if let leadingIcon = leadingIcon {
                Button(action: {
                    leadingAction?()
                }) {
                    Image(systemName: leadingIcon)
                        .font(.title2)
                        .foregroundColor(.primary)
                }
                .padding(.leading, 10)
            } else {
                Spacer().frame(width: 44)
            }

            Spacer()

            // Title (optional)
            if !showBackButton {
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
            }

            Spacer()

            // Trailing icon (optional)
            if let trailingIcon = trailingIcon {
                Button(action: {
                    trailingAction?()
                }) {
                    Image(systemName: trailingIcon)
                        .font(.title2)
                        .foregroundColor(.primary)
                }
                .padding(.trailing, 10)
            } else {
                Spacer().frame(width: 44)
            }
        }
        .frame(height: 44)
        .padding(.vertical, 10)
        .background(Color.clear)
    }
}

#Preview {
    VStack(spacing: 0) {
        CustomTopBarContent(
            title: "Preview",
            showBackButton: true,
            leadingAction: { print("Back tapped") },
            trailingAction: { print("Settings tapped") }
        )
        .padding(.top, 50)
        Spacer()
    }
    .background(Color(.systemGroupedBackground))
}
