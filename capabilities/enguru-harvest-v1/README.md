# ENGÜRÜ Yetenek Hasadı™ V1.1 — GitHub inceleme adayı

Kaynak: ENGÜRÜ Zülfikar™ V1.3, mevcut AGENTS.md ve canonical V3. Bu paket yardımcı yetenek adaptörüdür; yeni owner, issuer veya yönetişim çekirdeği kurmaz.

## Hedef

Altı kütüphane: skills, advanced_prompts, proven_sources, data_knowledge, engineering_recipes, evidence.

Akış: CANDIDATE → TESTED → PROVEN → ADOPTED. Ücretli API gereksinimi sıfır. Gerçek kaynak byte doğrulaması, lisans, güvenlik, tekrarlı test, gerçek görev, bağımsız inceleme ve insan yetkisi ayrı kapılardır.

## Sınırlar

Buradaki kayıtlardan hiçbiri dış kodu çalıştırmaz. 'PASS' şeklindeki beyanlar bağımsız doğrulamanın yerine geçmez; mevcut kapı sınıflayıcısı ilk çekirdektir. Haricî YouTube videosunun iki özgün yöntemi henüz teyit edilmedi. OSi saha, GitHub exact-head CI, bağımsız reviewer ve resmî DoneCheck ayrı HOLD kalır. Dış kaynaklar içeri alınmadan önce köken ve lisans doğrulanır.

## Test

`cd capabilities/enguru-harvest-v1 && python3 -B -m unittest -v test_harvest`

Gelecek kabul: gerçek 30 aday, 12 beceri, saha görevleri, üç gerçek simülasyon, exact-head CI ve bağımsız reviewer. Sadece sınıflayıcı testinden ürün tamamlanma hükmü çıkmaz.

Main korunur; bu dalın değişiklikleri bağımsız PR incelemesindedir.
