# -*- coding: utf-8 -*-
import json
import os

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
with open(os.path.join(base_dir, "poems.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

# Musical curation for poetry posts (chiaroscuro, neoclassical, ambient noir, post-rock)
soundtracks = [
    {"title": "On the Nature of Daylight", "artist": "Max Richter"},
    {"title": "Nuvole Bianche", "artist": "Ludovico Einaudi"},
    {"title": "Apocalypse", "artist": "Cigarettes After Sex"},
    {"title": "Written on the Sky", "artist": "Max Richter"},
    {"title": "Near Light", "artist": "Ólafur Arnalds"},
    {"title": "Una Mattina", "artist": "Ludovico Einaudi"},
    {"title": "Nocturne in C-Sharp Minor", "artist": "Frédéric Chopin"},
    {"title": "Experience", "artist": "Ludovico Einaudi"},
    {"title": "Familiar", "artist": "Agnes Obel"},
    {"title": "Gymnopédie No. 1", "artist": "Erik Satie"},
    {"title": "Says", "artist": "Nils Frahm"},
    {"title": "Saman", "artist": "Ólafur Arnalds"},
    {"title": "Divenire", "artist": "Ludovico Einaudi"},
    {"title": "Spiegel im Spiegel", "artist": "Arvo Pärt"},
    {"title": "Komorebi", "artist": "Fabrizio Paterlini"},
    {"title": "Riverside", "artist": "Agnes Obel"},
    {"title": "Sunset Lover", "artist": "Petit Biscuit"},
    {"title": "Leaves", "artist": "Ben Lukas Boysen"},
    {"title": "Time", "artist": "Hans Zimmer"},
    {"title": "Daylight", "artist": "David Kushner"},
    {"title": "I'll Keep Coming", "artist": "Low Roar"},
    {"title": "Svefn-g-englar", "artist": "Sigur Rós"},
    {"title": "Weightless", "artist": "Marconi Union"},
    {"title": "Petricor", "artist": "Ludovico Einaudi"},
    {"title": "Comptine d'un autre été", "artist": "Yann Tiersen"},
    {"title": "River Flows in You", "artist": "Yiruma"},
    {"title": "The Night", "artist": "Fabrizio Paterlini"},
    {"title": "Breathe", "artist": "Télépopmusik"},
    {"title": "Elegy for the Arctic", "artist": "Ludovico Einaudi"},
    {"title": "Particles", "artist": "Ólafur Arnalds"},
    {"title": "Avril 14th", "artist": "Aphex Twin"},
    {"title": "Light of the Seven", "artist": "Ramin Djawadi"},
    {"title": "Tomorrow's Song", "artist": "Ólafur Arnalds"},
    {"title": "Flora", "artist": "Ludovico Einaudi"},
    {"title": "Golden Hour", "artist": "JVKE"},
    {"title": "To Build a Home", "artist": "The Cinematic Orchestra"},
    {"title": "Oltremare", "artist": "Ludovico Einaudi"},
    {"title": "Vivaldi Recomposed: Spring 1", "artist": "Max Richter"},
    {"title": "Midnight City (Acoustic)", "artist": "M83"},
    {"title": "Sleeping at Last", "artist": "Saturn"},
    {"title": "A Walk", "artist": "Tycho"},
    {"title": "Fly", "artist": "Ludovico Einaudi"},
    {"title": "Silence", "artist": "Beethoven (Arr. Piano Noir)"},
    {"title": "Solemn Path", "artist": "Cuordivino Soundtrack"},
    {"title": "The Winner Is", "artist": "Mychael Danna"},
    {"title": "An Ending (Ascent)", "artist": "Brian Eno"},
    {"title": "Redemption", "artist": "Zack Hemsey"},
    {"title": "Versi Muti", "artist": "Refuso di Verso Theme"}
]

for i, poem in enumerate(data["poems"]):
    st = soundtracks[i % len(soundtracks)]
    poem["image"] = f"images/poesia_{poem['id']}.jpg"
    poem["musicTrack"] = st["title"]
    poem["musicArtist"] = st["artist"]
    poem["audioFile"] = f"audio/poesia_{poem['id']}.mp3"

# Update meta colors from purplish to chiaroscuro / light & shadows
data["meta"]["macroMoods"] = [
    {
        "key": "all",
        "name": "Tutti i Pensieri",
        "icon": "✦",
        "color": "#e0ded9",
        "desc": "Tutte le poesie dell'opera completa in chiaroscuro."
    },
    {
        "key": "ombra",
        "name": "L'Ombra e il Pozzo",
        "icon": "🌑",
        "color": "#7a7d85",
        "desc": "L'abisso dell'indifferenza, l'apatia, il fardello assillante, la serpe del dubbio e il silenzio."
    },
    {
        "key": "ardore",
        "name": "L'Ardore e la Carne",
        "icon": "🔥",
        "color": "#c4a373",
        "desc": "La bramosia profanatrice, il banco sacro violato, l'estasi dei corpi e il furore della mente."
    },
    {
        "key": "maschera",
        "name": "La Maschera e il Fango",
        "icon": "🎭",
        "color": "#94949e",
        "desc": "Il disprezzo del perbenismo, il riso beffardo, la foglia che cade senza pudore e il grido di ribellione."
    },
    {
        "key": "quiete",
        "name": "La Quiete e il Ritrovo",
        "icon": "🕯️",
        "color": "#e8d8be",
        "desc": "La moka del mattino, la brace che riarde, il paco e solenne pensare lungo il sentiero lineare."
    }
]

with open(os.path.join(base_dir, "poems.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open(os.path.join(base_dir, "data.js"), "w", encoding="utf-8") as f:
    f.write("const BOOK_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

print(f"Updated data with B&W photos and music tracks for all {len(data['poems'])} poems.")
