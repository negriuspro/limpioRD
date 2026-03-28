"""
Seed de todos los municipios de la República Dominicana.
Ejecutar: python seed_municipios.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limpiord.settings.development')
django.setup()

from ayuntamientos.models import Municipio

# (nombre, codigo, lat, lng)
MUNICIPIOS = [
    # ── Distrito Nacional ────────────────────────────────────────────────────
    ("Distrito Nacional",           "DN",   18.4861, -69.9312),

    # ── Santo Domingo ────────────────────────────────────────────────────────
    ("Santo Domingo Este",          "SDE",  18.4884, -69.8519),
    ("Santo Domingo Norte",         "SDN",  18.5400, -69.9800),
    ("Santo Domingo Oeste",         "SDO",  18.4900, -70.0100),
    ("Los Alcarrizos",              "SDA",  18.5100, -70.0500),
    ("Pedro Brand",                 "SDP",  18.5600, -70.0900),
    ("San Antonio de Guerra",       "SAG",  18.5000, -69.7700),
    ("Boca Chica",                  "BOC",  18.4511, -69.5997),
    ("San Luis",                    "SDL",  18.5100, -69.8300),
    ("Guerra",                      "GUE",  18.5300, -69.8100),

    # ── Santiago ─────────────────────────────────────────────────────────────
    ("Santiago de los Caballeros",  "STGO", 19.4517, -70.6970),
    ("Bisonó",                      "SGB",  19.4200, -70.9100),
    ("Jánico",                      "SGJ",  19.3200, -70.8300),
    ("Licey al Medio",              "SGL",  19.5000, -70.5800),
    ("San José de las Matas",       "SGM",  19.3300, -70.9300),
    ("Tamboril",                    "SGT",  19.4800, -70.6100),
    ("Villa González",              "SGV",  19.5100, -70.7500),
    ("Puñal",                       "SGP",  19.5300, -70.6800),
    ("Sabana Iglesia",              "SGS",  19.3700, -70.8700),

    # ── La Vega ──────────────────────────────────────────────────────────────
    ("La Vega",                     "LV",   19.2231, -70.5294),
    ("Constanza",                   "LVC",  18.9100, -70.7400),
    ("Jarabacoa",                   "LVJ",  19.1200, -70.6400),
    ("Jima Abajo",                  "LVI",  19.1600, -70.4800),

    # ── San Cristóbal ────────────────────────────────────────────────────────
    ("San Cristóbal",               "SC",   18.4152, -70.1053),
    ("Bajos de Haina",              "SCH",  18.4100, -70.0200),
    ("Cambita Garabitos",           "SCG",  18.3600, -70.1900),
    ("Los Cacaos",                  "SCC",  18.4900, -70.1900),
    ("Palenque",                    "SCP",  18.3400, -70.0100),
    ("San Gregorio de Nigua",       "SCN",  18.3800, -70.0600),
    ("Villa Altagracia",            "SCV",  18.6700, -70.1700),
    ("Yaguate",                     "SCY",  18.3400, -70.1400),

    # ── La Romana ────────────────────────────────────────────────────────────
    ("La Romana",                   "LR",   18.4273, -68.9728),
    ("Guaymate",                    "LRG",  18.5000, -69.0800),
    ("Villa Hermosa",               "LRV",  18.4700, -69.0000),

    # ── San Pedro de Macorís ─────────────────────────────────────────────────
    ("San Pedro de Macorís",        "SPM",  18.4536, -69.2964),
    ("Consuelo",                    "SPC",  18.5000, -69.3500),
    ("Guayacanes",                  "SPG",  18.4300, -69.4200),
    ("Juan Dolio",                  "SPJ",  18.4300, -69.4500),
    ("Los Llanos",                  "SPL",  18.6100, -69.5200),
    ("Ramón Santana",               "SPR",  18.5400, -69.2200),
    ("Quisqueya",                   "SPQ",  18.5500, -69.4000),

    # ── Puerto Plata ─────────────────────────────────────────────────────────
    ("Puerto Plata",                "PP",   19.7939, -70.6878),
    ("Altamira",                    "PPA",  19.6600, -70.8300),
    ("Guananico",                   "PPG",  19.7000, -70.7500),
    ("Imbert",                      "PPI",  19.7700, -70.8300),
    ("Los Hidalgos",                "PPH",  19.7500, -70.9300),
    ("Luperón",                     "PPL",  19.8900, -70.9600),
    ("Sosúa",                       "PPS",  19.7600, -70.5100),
    ("Villa Isabela",               "PPV",  19.8400, -71.0700),
    ("Montellano",                  "PPM",  19.7300, -70.7000),

    # ── La Altagracia ────────────────────────────────────────────────────────
    ("Higüey",                      "AG",   18.6153, -68.7078),
    ("San Rafael del Yuma",         "AGS",  18.4300, -68.6600),
    ("Bávaro",                      "AGB",  18.7100, -68.4500),
    ("Miches",                      "AGM",  18.9900, -69.0500),

    # ── Duarte ───────────────────────────────────────────────────────────────
    ("San Francisco de Macorís",    "DU",   19.3006, -70.2528),
    ("Arenoso",                     "DUA",  19.1600, -69.8200),
    ("Castillo",                    "DUC",  19.2100, -70.0100),
    ("Las Guáranas",                "DUG",  19.1900, -69.9800),
    ("Pimentel",                    "DUP",  19.1800, -70.1100),
    ("Villa Riva",                  "DUV",  19.1800, -69.9100),

    # ── Espaillat ────────────────────────────────────────────────────────────
    ("Moca",                        "ESP",  19.3953, -70.5256),
    ("Cayetano Germosén",           "ESC",  19.3700, -70.3700),
    ("Gaspar Hernández",            "ESG",  19.6200, -70.2700),
    ("Jamao al Norte",              "ESJ",  19.5400, -70.4300),

    # ── María Trinidad Sánchez ───────────────────────────────────────────────
    ("Nagua",                       "MT",   19.3800, -69.8500),
    ("Cabrera",                     "MTC",  19.6400, -69.9200),
    ("El Factor",                   "MTE",  19.4800, -69.7600),
    ("Río San Juan",                "MTR",  19.6300, -70.0800),

    # ── Samaná ───────────────────────────────────────────────────────────────
    ("Samaná",                      "SAM",  19.2061, -69.3364),
    ("Sánchez",                     "SAS",  19.2300, -69.6100),
    ("Las Terrenas",                "SAT",  19.3100, -69.5200),
    ("El Limón",                    "SAL",  19.2600, -69.3800),

    # ── Monte Plata ──────────────────────────────────────────────────────────
    ("Monte Plata",                 "MP",   18.8061, -69.7853),
    ("Bayaguana",                   "MPB",  18.7400, -69.6300),
    ("Peralvillo",                  "MPP",  18.8900, -70.0600),
    ("Sabana Grande de Boyá",       "MPS",  18.9400, -69.7900),
    ("Yamasá",                      "MPY",  18.7700, -70.0200),

    # ── Peravia ──────────────────────────────────────────────────────────────
    ("Baní",                        "PR",   18.2797, -70.3317),
    ("Nizao",                       "PRN",  18.2300, -70.2100),
    ("Matanzas",                    "PRM",  18.3000, -70.3700),

    # ── San Juan ─────────────────────────────────────────────────────────────
    ("San Juan de la Maguana",      "SJ",   18.8058, -71.2286),
    ("Bohechío",                    "SJB",  18.7700, -71.0000),
    ("El Cercado",                  "SJC",  18.7200, -71.5300),
    ("Juan de Herrera",             "SJH",  18.7200, -71.1800),
    ("Las Matas de Farfán",         "SJM",  18.8700, -71.5300),
    ("Vallejuelo",                  "SJV",  18.6700, -71.3300),

    # ── Azua ─────────────────────────────────────────────────────────────────
    ("Azua",                        "AZ",   18.4558, -70.7347),
    ("Estebanía",                   "AZE",  18.4200, -70.5600),
    ("Guayabal",                    "AZG",  18.3700, -70.8500),
    ("Las Charcas",                 "AZC",  18.5100, -70.9200),
    ("Las Yayas de Viajama",        "AZY",  18.3800, -70.7900),
    ("Padre Las Casas",             "AZP",  18.7300, -70.8800),
    ("Peralta",                     "AZR",  18.5800, -70.7400),
    ("Pueblo Viejo",                "AZV",  18.3100, -70.7600),
    ("Sabana Yegua",                "AZS",  18.4700, -71.0900),

    # ── Bahoruco ─────────────────────────────────────────────────────────────
    ("Neyba",                       "BH",   18.4772, -71.4192),
    ("Galván",                      "BHG",  18.4100, -71.5800),
    ("Los Ríos",                    "BHR",  18.5600, -71.5600),
    ("Tamayo",                      "BHT",  18.4600, -71.2300),
    ("Villa Jaragua",               "BHV",  18.3900, -71.6100),

    # ── Barahona ─────────────────────────────────────────────────────────────
    ("Barahona",                    "BR",   18.2131, -71.1011),
    ("Cabral",                      "BRC",  18.2500, -71.2200),
    ("El Peñón",                    "BRP",  18.2800, -71.1500),
    ("Enriquillo",                  "BRE",  17.9000, -71.2400),
    ("Fundación",                   "BRF",  18.3400, -71.1200),
    ("Jaquimeyes",                  "BRJ",  18.2100, -71.1600),
    ("La Ciénaga",                  "BRL",  18.1900, -71.1700),
    ("Las Salinas",                 "BRS",  18.2700, -70.9700),
    ("Paraíso",                     "BRR",  17.9800, -71.1700),
    ("Polo",                        "BRO",  18.1100, -71.2700),
    ("Vicente Noble",               "BRN",  18.3900, -71.1800),

    # ── Dajabón ──────────────────────────────────────────────────────────────
    ("Dajabón",                     "DJ",   19.5511, -71.7078),
    ("El Pino",                     "DJP",  19.5700, -71.5600),
    ("Loma de Cabrera",             "DJL",  19.4200, -71.6100),
    ("Partido",                     "DJR",  19.6400, -71.6500),
    ("Restauración",                "DJT",  19.3100, -71.6900),

    # ── Elías Piña ───────────────────────────────────────────────────────────
    ("Comendador",                  "EP",   18.8697, -71.7064),
    ("Bánica",                      "EPB",  18.9800, -71.7100),
    ("El Llano",                    "EPL",  18.7200, -71.5900),
    ("Hondo Valle",                 "EPH",  18.7100, -71.6700),
    ("Juan Santiago",               "EPJ",  18.8200, -71.7500),
    ("Pedro Santana",               "EPS",  18.7800, -71.8700),

    # ── El Seibo ─────────────────────────────────────────────────────────────
    ("El Seibo",                    "ES",   18.7658, -69.0383),
    ("Miches",                      "ESM",  18.9900, -69.0500),
    ("Pedro Sánchez",               "ESP2", 18.8700, -69.1900),

    # ── Hato Mayor ───────────────────────────────────────────────────────────
    ("Hato Mayor",                  "HM",   18.7650, -69.2608),
    ("El Valle",                    "HMV",  18.8900, -69.3700),
    ("Sabana de la Mar",            "HMS",  19.0700, -69.3900),

    # ── Hermanas Mirabal ─────────────────────────────────────────────────────
    ("Salcedo",                     "MI",   19.3800, -70.4200),
    ("Tenares",                     "MIT",  19.3700, -70.2800),
    ("Villa Tapia",                 "MIV",  19.3000, -70.4400),

    # ── Independencia ────────────────────────────────────────────────────────
    ("Jimaní",                      "IN",   18.4933, -71.8506),
    ("Cristóbal",                   "INC",  18.5600, -71.7900),
    ("Duvergé",                     "IND",  18.3700, -71.5300),
    ("La Descubierta",              "INL",  18.5600, -71.7200),
    ("Mella",                       "INM",  18.4200, -71.7100),
    ("Postrer Río",                 "INP",  18.3200, -71.6000),

    # ── Monseñor Nouel ───────────────────────────────────────────────────────
    ("Bonao",                       "MN",   18.9400, -70.4100),
    ("Maimon",                      "MNM",  18.8900, -70.2900),
    ("Piedra Blanca",               "MNP",  18.9300, -70.5100),

    # ── Monte Cristi ─────────────────────────────────────────────────────────
    ("Monte Cristi",                "MC",   19.8578, -71.6511),
    ("Castañuelas",                 "MCC",  19.7900, -71.5100),
    ("Guayubín",                    "MCG",  19.6900, -71.4200),
    ("Las Matas de Santa Cruz",     "MCL",  19.7400, -71.5100),
    ("Pepillo Salcedo",             "MCP",  19.9400, -71.7300),
    ("Villa Vásquez",               "MCV",  19.7600, -71.4400),

    # ── Pedernales ───────────────────────────────────────────────────────────
    ("Pedernales",                  "PE",   17.8547, -71.7447),
    ("Oviedo",                      "PEO",  17.8100, -71.4100),

    # ── Sánchez Ramírez ──────────────────────────────────────────────────────
    ("Cotuí",                       "SR",   19.0567, -70.1528),
    ("Cevicos",                     "SRC",  19.0100, -70.0100),
    ("Fantino",                     "SRF",  19.1400, -70.3400),
    ("La Mata",                     "SRL",  19.1600, -70.1300),

    # ── Santiago Rodríguez ───────────────────────────────────────────────────
    ("Sabaneta",                    "SK",   19.5467, -71.3469),
    ("Los Almácigos",               "SKA",  19.5100, -71.6000),
    ("Monción",                     "SKM",  19.4000, -71.1800),

    # ── Valverde ─────────────────────────────────────────────────────────────
    ("Mao",                         "VL",   19.5592, -71.0761),
    ("Esperanza",                   "VLE",  19.5500, -70.9800),
    ("Laguna Salada",               "VLL",  19.6700, -71.0600),

    # ── San José de Ocoa ─────────────────────────────────────────────────────
    ("San José de Ocoa",            "SO",   18.5442, -70.5053),
    ("Rancho Arriba",               "SOR",  18.5100, -70.5900),
    ("Sabana Larga",                "SOS",  18.4900, -70.6700),
]


def seed():
    created = 0
    updated = 0
    for nombre, codigo, lat, lng in MUNICIPIOS:
        obj, is_new = Municipio.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre':          nombre,
                'latitud_centro':  lat,
                'longitud_centro': lng,
            }
        )
        if is_new:
            created += 1
        else:
            # Actualizar nombre y coords si ya existia con datos distintos
            changed = False
            if obj.nombre != nombre:
                obj.nombre = nombre
                changed = True
            if float(obj.latitud_centro) != lat:
                obj.latitud_centro = lat
                changed = True
            if float(obj.longitud_centro) != lng:
                obj.longitud_centro = lng
                changed = True
            if changed:
                obj.save()
                updated += 1

    total = Municipio.objects.count()
    print(f"OK: {created} municipios creados, {updated} actualizados. Total en BD: {total}")


if __name__ == '__main__':
    seed()
