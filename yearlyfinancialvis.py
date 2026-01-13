import json
import webbrowser
import os
import math


def yatirim_kokpiti_ozel_glow():
    print("\n--- Requiem Yearly Financials ---\n")

    # --- 1. KULLANICI GİRDİLERİ ---
    try:
        ana_para = float(input("1. Yatırılacak Ana Para (TL): "))
        enflasyon_yillik = float(input("2. Türkiye Yıllık Enflasyon Beklentisi (%): "))
        gunluk_faiz_orani = float(input("3. Günlük Mevduat Faiz Oranı (Örn: 0.136) / (compound interest): "))

        print("\n--- DÖVİZ KUR BEKLENTİLERİ ---")
        dolar_artisi_yillik = float(input("4. Dolar Kuru Yıllık Artış Beklentisi (%): "))
        euro_artisi_yillik = float(input("5. Euro Kuru Yıllık Artış Beklentisi (%): "))

        print("\n--- YATIRIM ARAÇLARI GETİRİLERİ ---")
        bist100_getiri = float(input("6. BIST 100 Yıllık Getiri Beklentisi (TL BAZLI %): "))
        sp500_dolar_getiri = float(input("7. S&P 500 Yıllık Getiri (DOLAR BAZLI %): "))
        altin_dolar_getiri = float(input("8. Altın (Ons) Yıllık Getiri (DOLAR BAZLI %): "))

        print("\n--- KİŞİSEL PORTFÖY (Opsiyonel) ---")
        portfoy_input = input("9. Kendi Portföyünüzün Yıllık Getiri Hedefi (%) [Yoksa Enter'a bas]: ")

        portfoy_var = False
        portfoy_getiri = 0.0
        if portfoy_input.strip() and portfoy_input.lower() != "yok":
            portfoy_getiri = float(portfoy_input)
            portfoy_var = True

    except ValueError:
        print("Hata: Sadece sayı girmelisin.")
        return

    # --- 2. HESAPLAMALAR ---
    gunler = list(range(366))

    data_faiz = []
    data_enflasyon = []
    data_reel = []
    data_bist = []
    data_sp500 = []
    data_altin = []
    data_dolar = []
    data_euro = []
    data_portfoy = []

    k_enf = math.pow((1 + enflasyon_yillik / 100), (1 / 365))
    k_dolar = math.pow((1 + dolar_artisi_yillik / 100), (1 / 365))
    k_euro = math.pow((1 + euro_artisi_yillik / 100), (1 / 365))
    k_bist = math.pow((1 + bist100_getiri / 100), (1 / 365))
    k_sp500_usd = math.pow((1 + sp500_dolar_getiri / 100), (1 / 365))
    k_altin_usd = math.pow((1 + altin_dolar_getiri / 100), (1 / 365))

    k_portfoy = 0
    if portfoy_var:
        k_portfoy = math.pow((1 + portfoy_getiri / 100), (1 / 365))

    for gun in gunler:
        mevduat = ana_para * math.pow((1 + gunluk_faiz_orani / 100), gun)
        data_faiz.append(round(mevduat, 2))

        enf_tutar = ana_para * math.pow(k_enf, gun)
        data_enflasyon.append(round(enf_tutar, 2))

        data_reel.append(round(mevduat / math.pow(k_enf, gun), 2))

        data_bist.append(round(ana_para * math.pow(k_bist, gun), 2))

        kur_dolar_etkisi = math.pow(k_dolar, gun)
        data_sp500.append(round((ana_para * math.pow(k_sp500_usd, gun)) * kur_dolar_etkisi, 2))
        data_altin.append(round((ana_para * math.pow(k_altin_usd, gun)) * kur_dolar_etkisi, 2))
        data_dolar.append(round(ana_para * kur_dolar_etkisi, 2))
        data_euro.append(round(ana_para * math.pow(k_euro, gun), 2))

        if portfoy_var:
            data_portfoy.append(round(ana_para * math.pow(k_portfoy, gun), 2))

    # --- 3. HTML OLUŞTURMA ---

    portfoy_dataset_str = ""
    if portfoy_var:
        portfoy_dataset_str = f"""
                    {{
                        label: 'KİŞİSEL PORTFÖYÜM',
                        data: {json.dumps(data_portfoy)},
                        borderColor: '#000000', // SİYAH
                        borderWidth: 4,
                        pointRadius: 0,
                        tension: 0.3
                    }},
        """

    html_kodlari = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Requiem Yearly Financials</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; padding: 20px; }}
            .container {{ width: 95%; margin: 0 auto; }}
            h1 {{ text-align: center; color: #58a6ff; margin-bottom: 5px; }}
            h3 {{ text-align: center; color: #8b949e; margin-top: 0; font-weight: normal; font-size: 0.9em; }}
            .info-box {{ background: #161b22; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; border: 1px solid #30363d; font-size: 0.9em; }}
            canvas {{ background-color: #161b22; border-radius: 10px; padding: 10px; border: 1px solid #30363d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Requiem Yearly Financials</h1>
            <h3>github.com/RequiemLaw</h3>

            <div class="info-box">
                %YTD Başlangıç: <strong>{ana_para:,.0f} TL</strong> | Enflasyon: <strong>%{enflasyon_yillik}</strong> | Günlük Faiz: <strong>%{gunluk_faiz_orani}</strong>
                <br>
            </div>

            <canvas id="yatirimChart"></canvas>
        </div>

        <script>
            const ctx = document.getElementById('yatirimChart').getContext('2d');
            const gunler = {json.dumps(gunler)};

            // Genel Chart.js ayarları
            Chart.defaults.borderColor = '#30363d';
            Chart.defaults.color = '#c9d1d9';

            const data = {{
                labels: gunler,
                datasets: [
                    {{
                        label: 'MEVDUAT (TL)',
                        data: {json.dumps(data_faiz)},
                        borderColor: '#238636', // YEŞİL
                        borderWidth: 3, tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'ENFLASYON SINIRI',
                        data: {json.dumps(data_enflasyon)},
                        borderColor: '#da3633', // KIRMIZI
                        borderWidth: 2, borderDash: [5, 5], tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'REEL ALIM GÜCÜ (Net)',
                        data: {json.dumps(data_reel)},
                        borderColor: '#9e9e9e', // GRİ
                        backgroundColor: 'rgba(158, 158, 158, 0.3)', // GRİ DOLGU
                        borderWidth: 2, fill: true, tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'BIST 100 (TL)',
                        data: {json.dumps(data_bist)},
                        borderColor: '#ffffff', // BEYAZ (Düz, Glowsuz)
                        borderWidth: 2, tension: 0.3, pointRadius: 0
                    }},
                    {portfoy_dataset_str}
                    {{
                        label: 'S&P 500 (USD+Kur)',
                        data: {json.dumps(data_sp500)},
                        borderColor: '#58a6ff', // MAVİ
                        borderWidth: 2, tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'ALTIN (USD+Kur)',
                        data: {json.dumps(data_altin)},
                        borderColor: '#d29922', // ALTIN
                        borderWidth: 2, tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'SADECE DOLAR',
                        data: {json.dumps(data_dolar)},
                        borderColor: '#f0f6fc', // BEYAZ/AÇIK GRİ
                        borderWidth: 3, 
                        tension: 0.3, pointRadius: 0
                    }},
                    {{
                        label: 'EURO',
                        data: {json.dumps(data_euro)},
                        borderColor: '#a371f7', // MOR
                        borderWidth: 2, tension: 0.3, pointRadius: 0
                    }}
                ]
            }};

            const config = {{
                type: 'line',
                data: data,
                options: {{
                    responsive: true,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{ label += ': '; }}
                                    if (context.parsed.y !== null) {{
                                        label += new Intl.NumberFormat('tr-TR', {{ style: 'currency', currency: 'TRY', maximumFractionDigits: 0 }}).format(context.parsed.y);
                                    }}
                                    return label;
                                }}
                            }},
                            backgroundColor: 'rgba(22, 27, 34, 0.95)',
                            titleColor: '#58a6ff',
                            bodyColor: '#c9d1d9',
                            borderColor: '#30363d', borderWidth: 1
                        }},
                        legend: {{ labels: {{ color: '#c9d1d9' }} }}
                    }},
                    scales: {{
                        x: {{ title: {{ display: true, text: 'Gün', color: '#8b949e' }}, ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }},
                        y: {{ title: {{ display: true, text: 'Tutar (TL)', color: '#8b949e' }}, ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }}
                    }}
                }},
                plugins: [{{
                    id: 'glowEffect',
                    beforeDatasetDraw: (chart, args, options) => {{
                        const ctx = chart.ctx;
                        const dataset = chart.data.datasets[args.index];

                        // 1. KİŞİSEL PORTFÖY (SİYAH ÇİZGİ) -> BEYAZ GLOW
                        if (dataset.borderColor === '#000000') {{
                            ctx.save();
                            ctx.shadowColor = 'white';
                            ctx.shadowBlur = 15;
                            ctx.shadowOffsetX = 0;
                            ctx.shadowOffsetY = 0;
                        }}

                        // 2. DOLAR (BEYAZ ÇİZGİ) -> SİYAH GLOW (Daha belirgin olması için)
                        else if (dataset.borderColor === '#f0f6fc') {{
                            ctx.save();
                            ctx.shadowColor = 'black';
                            ctx.shadowBlur = 15;
                            ctx.shadowOffsetX = 0;
                            ctx.shadowOffsetY = 0;
                        }}
                    }},
                    afterDatasetDraw: (chart, args, options) => {{
                        const ctx = chart.ctx;
                        const dataset = chart.data.datasets[args.index];
                        // Eğer değişiklik yaptıysak geri al (restore)
                        if (dataset.borderColor === '#000000' || dataset.borderColor === '#f0f6fc') {{
                            ctx.restore();
                        }}
                    }}
                }}]
            }};

            new Chart(ctx, config);
        </script>
    </body>
    </html>
    """

    dosya_adi = "yatirim_kokpiti_final.html"
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(html_kodlari)

    print(f"\nTablo hazırlandı! '{dosya_adi}' dosyasını açıyorum...")
    webbrowser.open('file://' + os.path.realpath(dosya_adi))


if __name__ == "__main__":
    yatirim_kokpiti_ozel_glow()