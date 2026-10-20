
import Foundation
import Security
import LocalAuthentication

func fail(_ code: String) -> Never {
    print("STATE=HOLD_GUVENLI_DUR")
    print("BLOCKER=\(code)")
    exit(50)
}

let args = CommandLine.arguments
if args.count != 3 { fail("ARGUMENTS") }
let message = Data(args[1].utf8)
let keyTag = Data("org.enguru.plive.p02.g3a.secureenclave.p256.field.v1".utf8)
let acFlags: SecAccessControlCreateFlags = [.privateKeyUsage, .userPresence]
var acError: Unmanaged<CFError>?
guard let ac = SecAccessControlCreateWithFlags(kCFAllocatorDefault,
    kSecAttrAccessibleWhenUnlockedThisDeviceOnly, acFlags, &acError) else { fail("ACCESS_CONTROL") }
let context = LAContext()
context.localizedReason = "ENGÜRÜ P02.S01.01 saha imza kanıtı"
context.interactionNotAllowed = false
let query: [String: Any] = [
    kSecClass as String: kSecClassKey,
    kSecAttrApplicationTag as String: keyTag,
    kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
    kSecReturnRef as String: true,
    kSecUseAuthenticationContext as String: context
]
var item: CFTypeRef?
var status = SecItemCopyMatching(query as CFDictionary, &item)
var wasCreated = false
var privateKey: SecKey
if status == errSecItemNotFound {
    let attributes: [String: Any] = [
        kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
        kSecAttrKeySizeInBits as String: 256,
        kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
        kSecPrivateKeyAttrs as String: [
            kSecAttrIsPermanent as String: true,
            kSecAttrApplicationTag as String: keyTag,
            kSecAttrAccessControl as String: ac
        ]
    ]
    var createError: Unmanaged<CFError>?
    guard let created = SecKeyCreateRandomKey(attributes as CFDictionary, &createError) else {

        let underlyingError = createError?.takeRetainedValue()
        let domain = underlyingError.map {
            String(describing: CFErrorGetDomain($0))
        } ?? "NONE"
        let code = underlyingError.map {
            String(CFErrorGetCode($0))
        } ?? "NONE"
        fail("SECURE_ENCLAVE_CREATE_FAILED_DOMAIN_\(domain)_CODE_\(code)")
    }
    privateKey = created
    wasCreated = true
} else if status == errSecSuccess, let found = item {
    privateKey = found as! SecKey
} else { fail("KEYCHAIN_LOOKUP_\(status)") }

guard let publicKey = SecKeyCopyPublicKey(privateKey) else { fail("NO_PUBLIC_KEY") }
var error: Unmanaged<CFError>?
let algorithm = SecKeyAlgorithm.ecdsaSignatureMessageX962SHA256
if !SecKeyIsAlgorithmSupported(privateKey, .sign, algorithm) { fail("P256_SIGN_UNSUPPORTED") }
guard let signature = SecKeyCreateSignature(privateKey, algorithm, message as CFData, &error) as Data? else {
    fail("SIGN_CANCELLED_OR_FAILED")
}
var verifyError: Unmanaged<CFError>?
let verified = SecKeyVerifySignature(publicKey, algorithm, message as CFData, signature as CFData, &verifyError)
if !verified { fail("SIGNATURE_VERIFICATION_FAILED") }
var publicError: Unmanaged<CFError>?
guard let publicBytes = SecKeyCopyExternalRepresentation(publicKey, &publicError) as Data? else {
    fail("PUBLIC_EXPORT_FAILED")
}
// Public key alone is not an authorized OSi trust anchor.
let result: [String: Any] = [
    "state": "PASS_BOUNDED_SECURE_ENCLAVE_SIGNATURE_OBSERVATION_ONLY",
    "signatureValid": verified,
    "algorithm": "ECDSA_P256_SHA256_X962",
    "secureEnclaveRequested": true,
    "privateKeyExported": false,
    "keyCreatedDuringRun": wasCreated,
    "publicKeyX963Hex": publicBytes.map { String(format: "%02x", $0) }.joined(),
    "signatureDerHex": signature.map { String(format: "%02x", $0) }.joined(),
    "scope": args[2],
    "nativeAuthority": "HOLD",
    "verifiedFinish": "HOLD"
]
let json = try! JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
print(String(data: json, encoding: .utf8)!)
