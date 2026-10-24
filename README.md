# Zaman

Pomodoro, görevler, notlar, takvimler, ömür sayacı, alışkanlık takibi ve ekran
ayarı (mavi ışık / gri mod) içeren masaüstü uygulaması. Koyu gri tema, beyaz yazılar.

## Klasör yapısı

```
zaman/
├── zaman.py              Giriş noktası
├── zaman.space           Başlatıcı (bağımlılık kurar, çalıştırır, paketler)
├── build.sh              Tek dosyalık paket üretir (dist/zaman)
├── requirements.txt
├── ikon/kavram.png       Uygulama ikonu (mevcut projeden kopyalayın)
├── core/                 Çekirdek
│   ├── app.py            Pencere yöneticisi, sekmeler, tepsi, global zamanlayıcı
│   ├── storage.py        Veri (veri/veriler.json) ve referans saati
│   ├── theme.py          Tüm renkler (tek yerden değiştirilebilir)
│   ├── ui.py             Ortak buton, akış düzeni
│   ├── sound.py          Pomodoro zili
│   ├── pomodoro_engine.py
│   └── display/          Ekran sürücüleri
│       ├── controller.py Modların isteğini oturum sürücüsüne çevirir
│       ├── x11.py        xrandr gamma/parlaklık, CTM ve picom gölgelendirici (gri)
│       ├── wayland.py    gammastep (wlr-gamma-control destekleyen compositor'lar)
│       └── autostart.py  Oturum açılışında başlatma
└── modes/                Her mod ayrı dosya
    ├── __init__.py       Mod kayıt defteri (sıra burada)
    ├── base.py           ModeBase: tüm modların temel sınıfı
    ├── pomodoro.py       Mod 0
    ├── tasks.py          Mod 1
    ├── notes.py          Mod 2
    ├── calendar_normal.py Mod 3
    ├── calendar_numeric.py Mod 4
    ├── calendar_octal.py Mod 5
    ├── life.py           Mod 6
    ├── date_settings.py  Mod 7
    ├── screen.py         Mod 8
    └── habits.py         Mod 9
```

## Çalıştırma

```bash
./zaman.space            # ilk çalıştırmada sanal ortam ve PyQt5 kurulur
./zaman.space --kur      # sadece bağımlılıkları kur
```

Gereksinimler:
- **X11:** `xrandr` (zorunlu). Gri mod için `picom` (GLX) veya CTM destekli sürücü.
- **Wayland:** `gammastep` (ör. `sudo apt install gammastep`). Gri mod bu oturumda desteklenmez.

## Paketleme

```bash
./zaman.space --paketle   # veya ./build.sh
./dist/zaman              # tek dosyalık çalıştırılabilir
```

Paket, üretildiği platform için derlenir (Linux'ta Linux paketi).

## Yeni mod ekleme

1. `modes/yeni_mod.py` dosyası oluşturun, `ModeBase`'den türeyen `Mode` sınıfı yazın:

   ```python
   from modes.base import ModeBase

   class Mode(ModeBase):
       TITLE = "Yeni Mod"

       def build_ui(self):
           ...           # arayüzü kur; self.ctx üzerinden db, pomodoro, notes servislerine eriş

       def update_display(self):   # mod görünürken her saniye
           ...

       def tick(self):             # her zaman, her saniye (arka plan işleri)
           ...
   ```

2. `modes/__init__.py` içindeki `MODULES` listesine `"yeni_mod"` ekleyin.
   Hatalı bir mod uygulamayı çökertmez; sekmesinde hata mesajı gösterilir.

## Ekran ayarı notları

- Ekran değerleri yalnızca değiştiğinde donanıma gönderilir.
- Zamanlı mavi ışık ve gri mod, Ekran sekmesi açık olmasa da çalışır.
- Alt + V uygulamanın herhangi bir penceresinde ekranı varsayılana döndürür.
- Ayarlar `veri/veriler.json` içinde saklanır.
