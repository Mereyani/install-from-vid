# install-from-video

**Diğer diller:** [English](README.md) · [العربية](README.ar.md)

Bir Claude Code becerisi. Geliştirici aracı öneren bir reels gönderiyorsunuz; beceri size o
araçların gerçekte ne olduğunu söylüyor, var olduklarını kanıtlıyor ve kurulum komutlarını
elinize veriyor.

```
siz:    https://instagram.com/reel/…   "bundakileri kur"
beceri: ✓ 4 araç bulundu, 4'ü doğrulandı, 2'si zaten kurulu
        komutlar burada — çalıştıran sizsiniz
```

---

## Neden var

"En iyi 5 araç" videoları her yerde ve neredeyse hiçbiri bağlantı vermiyor. Videoyu
durdurmanız, bir depo adına gözlerinizi kısarak bakmanız ve onu kendiniz GitHub'a yazmanız
bekleniyor.

İşler tam da bu son adımda bozuluyor. Bir adı kulaktan yazıya dökmek sizi bir harf uzağınızda
sahte bir depoya götürür ve kurduğunuz bir eklenti, sonraki her oturumda kendi kancalarını
çalıştırır.

Bu beceri o boşluğu kapatır: dinler, ekranı okur, doğrular ve sonra **durur, kararı size
bırakır**.

## Onu farklı kılan ne

**Sizin makinenizde çalışır.** Klip, faster-whisper ile yerel olarak yazıya dökülür. API
çağrısı yok, yükleme yok, dakika başına ücret yok. Modele ulaşan tek şey sonuç üzerine
yürütülen akıl yürütmedir.

**Sadece sesi değil, ekranı da okur.** Herkesin atladığı kısım budur ve önemli olan tam da
budur — aşağıdaki tabloya bakın.

**Hiçbir şey kurmayı reddeder.** Video güvenilmez bir kaynaktır. Beceri komutları üretir,
onları bir insan çalıştırır.

**Tasarımı gereği ucuzdur.** Önce ses. Kareler yalnızca bir ad gerçekten belirsizse — çünkü
size asıl bağlam maliyeti çıkaran şey görüntülerdir, yazıya dökme değil.

## Tüm tasarımı haklı çıkaran tek tablo

Beceri dile bağlı değildir — dili kendisi algılar ve model doksan civarı dili kapsar.
Aşağıdaki örnek Arapça, çünkü ilk olarak onunla test edildi; aynı hata, içine yabancı ürün
adları serpiştirilmiş her anlatımda ortaya çıkar.

Aynı 59 saniyelik klip, iki farklı model boyutuyla:

| Söylenen | `whisper-small` | `whisper-large-v3` | Gerçeği |
|---|---|---|---|
| Agent Skills | `AgedSkills` ❌ | `agent skills` ✅ | `addyosmani/agent-skills` |
| OmniRoute | `أم نيروت` ❌ | `أومني راوت` ✅ | `diegosouzapw/OmniRoute` |
| Ponytail | `PonyTail` ⚠️ | `ponytail` ✅ | `DietrichGebert/ponytail` |
| sayılar | `"4.50%"` ❌ | `"22%"`, `"54%"` ✅ | %22 ve %54 |

GitHub'da `AgedSkills` aramak, 98 bin yıldızlı orijinali değil, sıfır yıldızlı kopyaları
getirir. Doğru ad **35,4. saniyedeki tek bir kareden** geldi; orada tarayıcının adres
çubuğunda `github.com/addyosmani/agent-skills` yazıyordu.

Ses size listenin şeklini verir. Ekran size adları verir. İkisine birden ihtiyacınız var.

## Kurulum

```bash
claude plugin marketplace add Mereyani/install-from-video
claude plugin install install-from-video@install-from-video
```

Ardından Python bağımlılıkları — Claude Code'un kullanacağı yorumlayıcıya:

```bash
python3 -m pip install yt-dlp faster-whisper pillow av
```

Yanlış yorumlayıcıyı seçerseniz betik size tam olarak hangi yorumlayıcıyı ve hangi pip
satırını kullanmanız gerektiğini söyler. Bu hata mesajı, deponun yazarı ona ilk kendisi
takıldığı için var.

Sonra Claude Code'u yeniden başlatın.

## Kullanım

Sadece bağlantıyı gönderin:

> bu videodaki eklentileri kur https://www.tiktok.com/@someone/video/…

Ya da `/install-from-video` ile doğrudan çağırın. yt-dlp'nin desteklediği her platform çalışır —
Instagram, TikTok, YouTube, X, Reddit.

## Nasıl çalışır

1. **Ses geçişi** — `yt-dlp` yalnızca sesi indirir (bir dakika için ~0,4 MB), `faster-whisper`
   onu işlemcide yazıya döker. Ücretsiz, yerel, token harcamaz.

2. **Kare geçişi, koşullu** — bir ad hâlâ belirsizse video indirilir ve ~40 kare, zaman
   damgalı kontakt sayfalarında döşenir. Bağlam maliyeti çıkaran adım budur; bu yüzden
   isteğe bağlıdır.

3. **Doğrulama** — her aday npm ve GitHub API'sine karşı kontrol edilir. `repository.url`
   alanı 404 veren bir paket, olası bir sahte ad olarak bildirilir.

4. **Kimliği çözme** — `plugin@marketplace` klonlanmış manifest'ten okunur; çünkü pazar
   yeri, deponun adıyla değil manifest'teki `name` alanıyla kaydedilir.

5. **Teslim** — her araç için bir `bash` bloğu ve neyin doğrulandığını gösteren bir tablo.

## Bu deponun zor yoldan öğrendiği üç şey

**Pazar yeri deponun adını almaz.** `claude plugin marketplace add`, onu
`.claude-plugin/marketplace.json` içindeki `name` alanıyla kaydeder. Yani
`thedotmack/claude-mem`, `claude-mem@thedotmack` olarak kurulur; `addyosmani/agent-skills`
ise `agent-skills@addy-agent-skills` olarak. Tahmin etmek her seferinde başarısız bir
kuruluma mal olur.

**Bir npm paketi artık var olmayan bir depoyu gösterebilir.** npm'deki
`obsidian-second-brain`, GitHub'da silinmiş bir depoya çözümleniyor; gerçek proje tamamen
başka bir sahibin altında yaşıyor. `repository.url` alanını her zaman okuyun ve her zaman
açın.

**Konuşma tanıma, tam da en çok acıtan yerde başarısız olur.** Bir dili yazıya döken model,
yabancı ürün adlarını sese göre yazar. Bu başarısızlık **sessizdir** — hata mesajı değil,
makul görünen bir kelime alırsınız. Onu yalnızca ekran düzeltir.

## Model seçimi

Varsayılan `large-v3` ve yukarıdaki tablolar bunun nedenidir. 8 çekirdekli bir Intel
işlemcide gerçek zamanın yaklaşık iki katı hızında çalışır — bir dakikalık klip yaklaşık iki
dakika sürer — ve ~4,8 GB RAM kullanır.

Ölçülen alternatifler ve neden kaybettikleri:

| Model | Karar |
|---|---|
| `small` | Tam da ihtiyacınız olan adları bozuyor. Tabloya bakın. |
| `medium` | Daha küçük ve gerçek test kliplerinde large-v3'ü hiç geçemedi. |
| `large-v3-turbo` | 6 kat hızlı ama Arapçada daha kötü (WER 40,05'e karşı 36,86). |
| `distil-large-v3` | Yalnızca İngilizce. Elendi. |

Yalnızca genel bir fikir istiyorsanız `--model` ile değiştirin.

İyileştirme gibi görünen ama olmayan iki şey: `cpu_threads=8` ayarı, CTranslate2'nin kendi
seçimine kıyasla **%8 daha yavaş** ölçüldü; sesi 0,9 katına yavaşlatmanın ise literatürde
güvenilir bir dayanağı yok — sorun tempo değil, dil değiştirme.

## Gereksinimler

Python 3.9+, `yt-dlp`, `faster-whisper`, `pillow`, `av`. ffmpeg gerekmez: ses kendi özgün
kapsayıcısında indirilir ve asla yeniden kodlanmaz — bu hem daha basit hem de mp3'e
dönüştürmekten daha doğrudur.

İlk çalıştırma `large-v3` ağırlıklarını indirir (~2,4 GB), sonra önbelleğe alır.

## Sınırlar

- Videonun hiç söylemediği bir adı çıkaramaz. İçerik üreticisi "ikinci araç" deyip onu hiç
  göstermediyse, beceri tahmin etmek yerine bunu söyler.
- Giriş duvarı arkasındaki veya DRM korumalı gönderiler indirilemez.
- Yazıya dökme kalitesi, sonraki her şeyin tavanını belirler.

## Sorumlu kullanım

Bu araç, başkasının yayımladığı bir şeyin kopyasını indirir; bu yüzden birkaç noktayı açıkça
söylemekte fayda var.

- **Okumak için, yeniden yayımlamak için değil.** Ses ve kareler geçici çalışma dosyalarıdır.
  İşiniz bitince silin — pakete dâhil `.gitignore` onları varsayılan olarak git dışında tutar.
- **Platformun şartlarına saygı gösterin.** Bazı siteler otomatik indirmeyi kısıtlar. Kayıt
  olurken kabul ettiğiniz şartlar, verdiğiniz bir sözdür; ona uyun. Bu araç giriş duvarlarını
  veya DRM'i aşmaz ve aşmaya çalışmaz.
- **İçerik üreticisine hakkını verin.** Bir öneri işinize yaradıysa, onu bulma emeğini klibi
  yapan kişi vermiştir. Kaynağını belirtin.
- **Projeler başkalarına ait.** Üzerlerine bir şey inşa etmeden önce lisanslarını okuyun ve
  atıflarını olduğu gibi bırakın.

## Lisans

MIT
