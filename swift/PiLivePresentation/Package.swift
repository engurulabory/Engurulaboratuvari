// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "PiLivePresentation", platforms: [.macOS(.v13)], products: [.library(name: "PiLivePresentation", targets: ["PiLivePresentation"])], targets: [.target(name: "PiLivePresentation"), .testTarget(name: "PiLivePresentationTests", dependencies: ["PiLivePresentation"], resources: [.copy("Fixtures")])])
