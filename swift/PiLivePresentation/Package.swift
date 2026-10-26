// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "PiLivePresentation", platforms: [.macOS(.v13)], products: [.executable(name: "PiLive", targets: ["PiLiveApp"]), .library(name: "PiLivePresentation", targets: ["PiLivePresentation"])], targets: [.target(name: "PiLivePresentation"), .executableTarget(name: "PiLiveApp", dependencies: ["PiLivePresentation"]), .testTarget(name: "PiLivePresentationTests", dependencies: ["PiLivePresentation"], resources: [.copy("Fixtures")])])
