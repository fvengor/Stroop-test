# -*- coding: utf-8 -*-
#
# Proje Adı: Basit Stroop Testi - Furkan POLAT
# Amacı: Stroop Etkisini ölçmek için sadeleştirilmiş betik.
# Not: PsychoPy'ın kurulu olduğundan emin olun.
# -----------------------------------------------------------------------------------

from psychopy import visual, core, event, data, gui
import random
import os
from datetime import datetime
import time

# ----------------------- [Ayarlar ve Sabitler] -----------------------

# 1. Katılımcı Bilgisi (GUI'den alınacak)
katilimci_bilgi = {"ID": "Furkan_P", "Yas": 23}

# 2. Uyaran Tanımları
RENK_ISIMLERI = ["KIRMIZI", "YESIL", "MAVI", "SARI"]

# Kelime rengi (mürekkep) kodları
RENK_KODLARI = {
    "KIRMIZI": "red",
    "YESIL": "green",
    "MAVI": "blue",
    "SARI": "yellow"
}

# 3. Tuş Eşleşmeleri (Hangi tuş hangi renge karşılık geliyor?)
TUS_YANITLARI = {
    'r': 'KIRMIZI',
    'g': 'YESIL',
    'b': 'MAVI',
    'y': 'SARI'
}

# 4. Deneme Ayarları
PRATIK_SAYISI = 10
ANA_DENEME_SAYISI = 60
MAX_RT = 2.5        # Maksimum yanıt süresi (saniye)
GERIBILDIRIM_SURESI = 0.5
FIXATION_SURESI = 0.4 # + işaretinin kalma süresi

VERI_KLASORU = 'stroop_sonuclari'

# --------------------- [GUI ve Ortam Kurulumu] ---------------------

# Katılımcı ID'sini alıyoruz
dlg = gui.DlgFromDict(dictionary=katilimci_bilgi, title='Stroop Testi')
if not dlg.OK:
    core.quit()

k_id = katilimci_bilgi['ID']
k_yas = katilimci_bilgi['Yas']

# Veri klasörünü oluştur
if not os.path.exists(VERI_KLASORU):
    os.makedirs(VERI_KLASORU)

# Dosya adını hazırlıyoruz
zaman_damgasi = datetime.now().strftime('%Y%m%d_%H%M')
dosya_yolu = os.path.join(VERI_KLASORU, f"stroop_{k_id}_{zaman_damgasi}.csv")

# Pencereyi açıyoruz
win = visual.Window(size=(1024, 768), color='gray', units='norm', fullscr=False)

# Talimatlar
instr_text = (
    "Stroop Testine Hoş Geldiniz!\n\n"
    "Ekranda yazan kelimenin **MÜREKKEP RENGİNE** göre tuşa basın:\n"
    f" R: {TUS_YANITLARI['r']}, G: {TUS_YANITLARI['g']}, B: {TUS_YANITLARI['b']}, Y: {TUS_YANITLARI['y']}\n\n"
    f"Toplam {PRATIK_SAYISI} pratik ve {ANA_DENEME_SAYISI} ana deneme yapılacaktır.\n"
    "Başlamak için herhangi bir tuşa basın."
)
instr = visual.TextStim(win, text=instr_text, height=0.045, wrapWidth=1.5)
instr.draw()
win.flip()
event.waitKeys()


# ----------------------- [Fonksiyon Tanımları] -----------------------

def deneme_listesi_hazirla(sayi, renkler):
    """ Uyumlu/uyumsuz denemeleri eşit oranla hazırlar. """
    denemeler = []
    
    # Her bir kelime-renk çiftini (uyumlu ve uyumsuz) döngüde oluştur
    for kelime in renkler:
        # 1. Uyumlu (Congruent)
        denemeler.append({
            'kelime': kelime,
            'ink_code': RENK_KODLARI[kelime],
            'tip': 'uyumlu'
        })
        
        # 2. Uyumsuz (Incongruent)
        mumkun_murekkep = [r for r in renkler if r != kelime]
        rastgele_murekkep = random.choice(mumkun_murekkep)
        
        denemeler.append({
            'kelime': kelime,
            'ink_code': RENK_KODLARI[rastgele_murekkep],
            'tip': 'uyumsuz'
        })

    # İstenen sayıya ulaşmak için kes veya kopyala
    # Basitlik için sadece 50% uyumlu 50% uyumsuz oluşturup karıştırıp keselim
    random.shuffle(denemeler)
    return denemeler[:sayi]


def denemeyi_calistir(trial_list, block_name):
    """ Deneme listesini ekranda gösterir, verileri kaydeder. """
    sonuclar = []

    for t in trial_list:
        # + gösterimi
        fixation = visual.TextStim(win, text='+', height=0.15, color='black')
        fixation.draw()
        win.flip()
        core.wait(FIXATION_SURESI)
        
        # Uyaran gösterimi
        stimulus = visual.TextStim(win, text=t['kelime'],
                                 color=t['ink_code'],
                                 height=0.18)
        stimulus.draw()
        win.flip()
        
        t0 = core.getTime()
        keys = event.waitKeys(maxWait=MAX_RT, keyList=list(TUS_YANITLARI.keys()), timeStamped=True)
        
        RT = None
        yanit_renk_adi = None
        dogru = False
        
        if keys:
            tus, zaman = keys[0]
            RT = zaman - t0
            yanit_renk_adi = TUS_YANITLARI.get(tus)
            
            # Doğruluk Kontrolü: Mürekkep rengi adını bulma
            dogru_cevap_adi = None
            for isim, kod in RENK_KODLARI.items():
                if kod == t['ink_code']:
                    dogru_cevap_adi = isim
                    break
            
            # Karşılaştırma
            dogru = (yanit_renk_adi == dogru_cevap_adi)
            
        # Geri Bildirim
        if keys:
            fb_text = 'DOGRU' if dogru else 'YANLIS'
        else:
            fb_text = 'Geciktin!'

        feedback = visual.TextStim(win, text=fb_text, height=0.10)
        feedback.draw()
        win.flip()
        core.wait(GERIBILDIRIM_SURESI)
        
        # Sonucu kaydetme
        sonuclar.append({
            'blok': block_name,
            'katilimci_ID': k_id,
            'yas': k_yas,
            'kelime': t['kelime'],
            'murekkep': t['ink_code'],
            'tip': t['tip'],
            'kullanici_yaniti': yanit_renk_adi,
            'RT_sn': RT,
            'dogruluk': dogru
        })
        
        event.clearEvents()
    return sonuclar

# ----------------------- [Deney Akışı] -----------------------

# Pratik Bölümü Başlat
pratik_set = deneme_listesi_hazirla(PRATIK_SAYISI, RENK_ISIMLERI)
visual.TextStim(win, text='Pratik Başladı.').draw()
win.flip()
event.waitKeys()
pratik_sonuclari = denemeyi_calistir(pratik_set, 'pratik')

# Ana Deney Bölümü Başlat
visual.TextStim(win, text='Pratik bitti. Ana Deney Başlıyor.').draw()
win.flip()
event.waitKeys()
ana_set = deneme_listesi_hazirla(ANA_DENEME_SAYISI, RENK_ISIMLERI)
ana_sonuclari = denemeyi_calistir(ana_set, 'ana')

# ----------------------- [Veri Kaydı ve Kapanış] -----------------------

tum_sonuclar = pratik_sonuclari + ana_sonuclari

# CSV Başlıkları
alanlar = ['blok', 'katilimci_ID', 'yas', 'kelime', 'murekkep', 'tip', 'kullanici_yaniti', 'RT_sn', 'dogruluk']

# Dosyaya Yazma
with open(dosya_yolu, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=alanlar)
    writer.writeheader()
    writer.writerows(tum_sonuclar)

# Kapanış mesajı
visual.TextStim(win, text='Deney Tamamlandı. Veriler kaydedildi. Teşekkürler!').draw()
win.flip()
core.wait(2.0)

win.close()
core.quit()