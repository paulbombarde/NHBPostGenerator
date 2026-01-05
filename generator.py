import os.path
import xml.etree.ElementTree as ET
import subprocess
from copy import deepcopy
from datetime import date

from ics import Calendar
import sys
from collections import defaultdict
from collections import namedtuple
from base64 import b64encode
from PIL import Image

inkscape_path = '/Applications/Inkscape.app/Contents/MacOS/inkscape'
label_key = '{http://www.inkscape.org/namespaces/inkscape}label'
span_tag = '{http://www.w3.org/2000/svg}tspan'
href_tag = "{http://www.w3.org/1999/xlink}href"

team_text_marker = "NHB"
team_text_color = "#e0038c"
other_team_text_color = "#ffffff"

svg_template_folder = 'templates'
teams_logos_folder = 'logos_clubs'
svg_output_folder = 'outputs/svg'
png_output_folder = 'outputs/png'

week_days = ["LUNDI",
            "MARDI",
            "MERCREDI",
            "JEUDI",
            "VENDREDI",
            "SAMEDI",
            "DIMANCHE"]

months = ["JANVIER",
          "FEVRIER",
          "MARS",
          "AVRIL",
          "MAI",
          "JUIN",
          "JUILLET",
          "AOUT",
          "SEPTEMBRE",
          "OCTOBRE",
          "NOVEMBRE",
          "DECEMBRE"]

team_ics_name = "Nyon HandBall La Côte"
teams_replacements = {
    "Nyon HandBall La Côte": "NHB La Côte",
    "Lausanne-Ville/Cugy Handball": "LVC Handball",
    "Lausanne-Ville/Cugy Handball 2": "LVC Handball 2",
    "Lancy Plan-les-Ouates Hb": "Lancy PLO",
    "SG Genève Paquis - Lancy PLO": "Genève Paquis - Lancy",
    "SG Genève /TCGG/ Nyon": "SG Genève/TCGG/Nyon",
    "SG Wacker Thun 2 / Steffisburg": "Wacker Thun/Steffisburg",
    "SG Troinex / Chênois Genève": "SG Troinex/Chênois",
    "CS Chênois Genève Handball": "Chênois Genève HB",
    "RG Chênois Genève / Troinex": "Chênois Genève / Troinex",
    "- RG Chênois Genève / Troinex": "Chênois Genève / Troinex",
    "HBC Etoy 1 -": "HBC Etoy",
    "RG Rive Gauche Handball": "RG Rive Gauche HB",
    "HBC Vallée de Joux ° -": "HBC Vallée de Joux",
    "HBC Moudon -": "HBC Moudon"
}

level_replacements = {
    "M15G-P S1-06": "M15P",
    "M13G-P S1-06": "M13P",
    "M13G-P S1-08": "M13P-S1",
    'MU13P S1-07': 'M13P-S1',
    'M13G-P S1-07': 'M13P-S1',
    "MU13P S2-14": "M13P-S2",
    "M13G-P S2-14": "M13P-S2",
    'MU17P S1-07': "M17P",
    'M17G-P S1-07': "M17P",
    "H1-03": "1ière Ligue Hommes",
    'M2-06': "Ligue 2 Hommes",
    'H2-06': "Ligue 2 Hommes",
    "H4-09": "H4",
    "M14F-P-06": "M14P",
    'M14F-P-02 Prm': "M14P",
    'M14F-I Rlg-02': "M14I",
    'FU14I-03': "M14I",
    'M14F-I-03': "M14I",
    "M16F-P-08": "M16P",
    "M16F-P-06": "M16P",
    'FU16I-03': "M16I",
    'M16F-I-03': "M16I",
    "M16F-P-02 Prm" : "M16P",
    "D3-08": "3ième Ligue Dames",
    "F3-08": "Ligue 3 Dames",
    "Cup Mobilière H - Tour de qualification": "Cup Mobilière H",
    "Cup R H": "Cup R H - 1/8",
    "Cup R D": "Cup R D",
    'Cup R M15 G':'Cup R M15 G',
    'R-Cup M':'R-Cup M',
    'M15G-P S1-05 Prm': 'M15 Barrages',
    'M15G-I Rlg-02': "M15I",
    'M14F-P-08': "M14P",
    'M17G-P S1-08': "M17P",
    'M15G-P S2-12': "M15P",
    'M14F E/I-01': "M14E/I",
    'M13G-P S2-12': "M13P",
    'Cup R M16 F': "R Cup",
}

teams_logos={
    "NHB La Côte": "NHB.png",
    "LVC Handball": "LVC.png",
    "LVC Handball 2": "LVC.png",
    "KTV Visp Handball": "Visp.png",
    'Handball Oberaargau': "HVH.png",
    "SG TV Solothurn": "TV_Solothurn.png",
    "SG WEST Crissier": "crissier.png",
    "SG TV Birsfelden": "TVBirsfelden.png",
    'TV Pratteln NS 1': "NSPratteln.png",
    "Wacker Thun/Steffisburg": "Wacker_Thun.png",
    "HBC Neuchâtel": "Neuchatel.png",
    "HBC Moudon": "HBCMoudon.png",
    "PSG Lyss F3": "PSGLyss.png",
    "SG Vaud La Côte 2": "HBC - Nyon.png",
    "HBC Etoy": "etoy.png",
    "SG Möhlin/Magden": "Mohlin.png",
    "SG Nyon": "HBC - Nyon.png",
    "HS Biel Bienne": "HS Bienne.png",
    'RG Vaud La Côte 1': "tcgg.png",
    'RG Crissier-West M23': "crissier.png",
    'SG Bern City': "sgberncity.png",
    'HBC La Chaux-de-Fonds': "hbc-cdf.png",
    'SG US Yverdon / RSB': 'usyverdon.png',
    'RG Rive Gauche Handball': 'Rive_gauche1.png',
    'RG Rive Gauche HB': 'Rive_gauche1.png',
    'RG Vaud La Côte 2': "tcgg.png",
    'HG Bödeli': "hg-bodeli.png",
    'BSV Bern 3': "BSVBern.png",
    'HC Servette 1': 'Servette_hbc_logo.png',
    'SG TV Steffisburg 2 / Wacker':  "tvsteffisburg.png",
    'HC Vevey 1': "vevey.png",
}

players = {
    2: "Thomas Wagner",
    3: "Maël Céron",
    4: "Loïc Mazzoni",
    7: "Daniel Hardy",
    9: "Anatole Barraine",
    10: "Hippolyte Barraine",
    14: "Guilhem Rozier",
    15: "Gergo Bardos",
    16: "Oussama Medahi",
    17: "Aladin Pearzic",
    20: "Ramzi Hadjadj-Aoul",
    21: "Massimo Campanile",
    25: "Victor Le Bot",
    28: "Kenny Etenna",
    29: "Mohamed Bellayachi",
    39: "Fabio Campanile",
    92: "Rayane Souni",
    96: "Fares Froom"
}

def update_color(style_elem, html_color):
    if style_elem.startswith("fill:"):
        return "fill:"+html_color
    else:
        return style_elem


def replace_color(style, html_color):
    orig_elems = style.split(';')
    updated_elems = (update_color(elem, html_color) for elem in orig_elems)
    return ';'.join(updated_elems)


def replace_all(tree, replacements):
    try:
        for label, new_text in replacements.items():
            if tree.attrib[label_key] == label:
                for child in tree:
                    if not child.tag == span_tag:
                        continue

                    child.text = replacements.pop(label)
                    if "team" in label:
                        color = team_text_color if team_text_marker in child.text else other_team_text_color
                        child.attrib["style"] = replace_color(child.attrib["style"], color)
                    break
                return
    except KeyError:
        pass

    for child in tree:
        replace_all(child, replacements)
        if not replacements:
            return

def update_template(template_name, date, _replacements, png=True, write=True):
    replacements = deepcopy(_replacements)

    output_name = date+'_'+template_name
    svg_template = os.path.join(svg_template_folder, template_name)+".svg"
    svg_output = os.path.join(svg_output_folder, output_name+".svg")

    svg = ET.parse(svg_template)
    svg_root = svg.getroot()
    replace_all(svg_root, replacements)
    replace_logos(svg_root, _replacements)

    if write:
        svg.write(svg_output)
        if png:
            convert_to_png(svg_output)

    return svg_output

def convert_to_png(svg_file):
    output_name = os.path.split(svg_file)[-1][:-4]+".png"
    png_output = os.path.join(png_output_folder, output_name)
    subprocess.run([inkscape_path, '-w', '1080', '-o', png_output, svg_file])

Match = namedtuple('Match', ['time', 'place', 'level', 'team1', 'team2'])

def normalize_team(t):
    t1 = t.strip(" *°")
    try:
        return teams_replacements[t1]
    except KeyError:
        return t1


def normalize_level(l):
    return level_replacements[l]


def parse_match(ics_event):
    time = ics_event.begin.format("HH:mm")
    p1 = ics_event.name.find(" - ")
    p2 = ics_event.name.find(team_ics_name)
    if p2 == p1 + 3:
        t1 = team_ics_name
        t2 = ics_event.name[p2 + len(team_ics_name)  + 3:]
    else:
        t1 = ics_event.name[p1 + 3:-(len(team_ics_name)  + 3)]
        t2 = team_ics_name
    return Match(time, ics_event.location, ics_event.name[:p1], normalize_team(t1), normalize_team(t2))


def convert_date(date):
    week_day = date.weekday()
    week_day = week_days[week_day]
    month_day = str(date.day)
    month = months[date.month - 1]
    return " ".join([week_day, month_day, month])


def parse_calendar(ics_file_path):
    with open(ics_file_path) as ics_file:
        calendar = Calendar(ics_file.read())

    dates_to_matches = defaultdict(list)
    for event in calendar.events:
        if 'Nyon Handball - La Côte' in event.name:
            event.name = event.name.replace('Nyon Handball - La Côte', 'Nyon HandBall La Côte')

        if not 'Nyon HandBall La Côte' in event.name:
            continue

        date = event.begin.date()
        dates_to_matches[date].append(parse_match(event))

    return dates_to_matches


def replacements_from_hd_match(match, id):
    base = "match"+str(id)+"-"
    return {
        base+"team1": match.team1,
        base+"team2": match.team2,
        base+"time": match.time,
        base+"place": match.place,
    }


def replacements_from_match(match, id):
    t1 = match.team1
    t2 = match.team2
    if t1.startswith(team_text_marker):
        t1 += "-"+normalize_level(match.level)
    else:
        t2 += "-" + normalize_level(match.level)

    base = "match"+str(id)+"-"
    return {
        base+"team1": t1,
        base+"team2": t2,
        base+"time": match.time + ' - ' + match.place,
    }


def generate_posts(dates_to_matches, start= date.today()):
    for date, matches in dates_to_matches.items():
        if date < start:
            print("Skipping date ", date)
            continue

        other_matches = []
        for match in matches:
            if match.level.startswith("M2") or match.level.startswith("H2"):
                generate_post_h1(match, date)
            elif match.level.startswith("F3") or match.level.startswith("D3"):
                generate_post_d3(match, date)
            else:
                other_matches.append(match)

        if 4 < len(other_matches):
            # more than 4 matches on the same image would be ugly
            # We try first to separate at home games for external ones
            home_games = [g for g in other_matches if team_text_marker in g.team1]
            ext_games = [g for g in other_matches if team_text_marker in g.team2]
            if len(home_games) < 5 and len(ext_games) < 5:
                # Ok, let's generate them now
                generate_other_posts(home_games, date, "_home_")
                generate_other_posts(ext_games, date, "_ext_")
            else:
                matches.sort(key=lambda m: m.time)
                generate_other_posts(matches[:len(matches)//2], date, "_1_")
                generate_other_posts(matches[len(matches)//2:], date, "_2_")
        else:
            generate_other_posts(other_matches, date)

def generate_post_h1(match, date):
    rs = {"date": convert_date(date)}
    rs |= replacements_from_hd_match(match, 1)
    update_template('story_match_day', date.isoformat(), rs)
    update_template('match_day_h1', date.isoformat(), rs)
    update_template('results_h1', date.isoformat(), rs, False)
    update_template('story_players', date.isoformat(), rs, False)

def generate_post_d3(match, date):
    rs = {"date": convert_date(date)}
    rs |= replacements_from_hd_match(match, 1)
    update_template('story_match_day_dames', date.isoformat(), rs)
    update_template('match_day_d3', date.isoformat(), rs)
    update_template('results_d3', date.isoformat(), rs, False)

def generate_other_posts(matches, date, extra_name=""):
    if not matches:
        return
    rs = {"date": convert_date(date)}
    md_template = "match_day_" + str(len(matches))
    r_template = "results_" + str(len(matches))
    matches.sort(key=lambda m: m.time)
    for i, match in enumerate(matches, start=1):
        rs |= replacements_from_match(match, i)
    update_template(md_template, date.isoformat()+extra_name, rs)
    update_template(r_template, date.isoformat()+extra_name, rs, False)

def replace_logos(svg_tree, _replacements):
    for logo_label, team_label in [("match1-logo-team1", "match1-team1"), ("match1-logo-team2", "match1-team2")]:
        img = find_image(svg_tree, logo_label)
        if img is None:
            continue

        logo = teams_logos[_replacements[team_label]]
        logo = os.path.join(teams_logos_folder, logo)
        if not os.path.exists(logo):
            raise Exception("Could not find logo file ", logo)

        replace_logo(img, logo)

def replace_logo(svg_image, image_path):
    img = Image.open(image_path)
    svg_height = float(svg_image.attrib['width']) * img.height / img.width
    svg_dy = 0.5 * (float(svg_image.attrib['height']) - svg_height)
    svg_y = float(svg_image.attrib['y']) + svg_dy
    svg_image.attrib["y"] = str(svg_y)
    svg_image.attrib["height"] = str(svg_height)

    with open(image_path, "rb") as image_file:
        svg_image.attrib[href_tag] ='data:image/png;base64,'+ str(b64encode(image_file.read()), encoding='utf-8')


def find_image(svg, image_label):
    try:
        if svg.attrib[label_key] == image_label:
            return svg
    except KeyError:
        pass

    for child in svg:
        img = find_image(child, image_label)
        if not img == None:
            return img

    return None


if __name__ == "__main__":
    os.makedirs(svg_output_folder, exist_ok=True)
    os.makedirs(png_output_folder, exist_ok=True)

    matches = parse_calendar(sys.argv[1])
    generate_posts(matches)


