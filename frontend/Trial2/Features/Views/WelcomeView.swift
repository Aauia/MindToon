import SwiftUI
// MARK: - WelcomeView
struct WelcomeView: View {
    @StateObject var viewModel: WelcomeViewModel
    @ObservedObject var navigation: NavigationViewModel

    init(viewModel: WelcomeViewModel, navigation: NavigationViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
        self.navigation = navigation
    }

    var body: some View {
        VStack(spacing: 20) {
            Spacer()

            Text(viewModel.appTitle)
                .font(.largeTitle)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
                .foregroundColor(.primary)

            Text(viewModel.appSubtitle)
                .font(.title2)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)

            Text(viewModel.welcomeMessage)
                .font(.body)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
                .foregroundColor(.secondary)

            Spacer()

            Button(action: {
                navigation.currentScreen = .login
            }) {
                Text(viewModel.mainCallToAction)
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.purple)
                    .cornerRadius(15)
            }
            .padding(.horizontal, 40)
            .padding(.bottom, 50)
        }
        .padding()
                        .background(Color(red: 1.0, green: 1.0, blue: 0.9))
    }
}

// MARK: - Preview
struct WelcomeView_Previews: PreviewProvider {
    static var previews: some View {
        WelcomeView(viewModel: WelcomeViewModel(), navigation: NavigationViewModel())
    }
}
