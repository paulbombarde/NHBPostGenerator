import os.path
import xml.etree.ElementTree as ET
import subprocess
from ics import Calendar
import sys
from collections import defaultdict
from collections import namedtuple

inkscape_path = '/Applications/Inkscape.app/Contents/MacOS/inkscape'
label_key = '{http://www.inkscape.org/namespaces/inkscape}label'
span_tag = '{http://www.w3.org/2000/svg}tspan'

team_text_marker = "NHB"
team_text_color = "#e0038c"
other_team_text_color = "#ffffff"

svg_template_folder = 'templates'
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
    "Lancy Plan-les-Ouates Hb": "Lancy PLO",
    "SG Genève Paquis - Lancy PLO": "Genève Paquis - Lancy"
}

level_replacements = {
    "M15G-P S1-06": "M15P",
    "M13G-P S1-06": "M13P",
    "H1-03": "1ière Ligue Hommes",
    "H4-09": "H4",
    "M14F-P-06": "M14P",
    "M16F-P-08": "M16P",
    "D3-08": "3ième Ligue Dames",
    "Cup Mobilière H - Tour de qualification": "Cup Mobilière H"
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

def update_template(template_name, date, replacements, png=True):
    output_name = date+'_'+template_name
    svg_template = os.path.join(svg_template_folder, template_name)+".svg"
    svg_output = os.path.join(svg_output_folder, output_name+".svg")

    svg = ET.parse(svg_template)
    svg_root = svg.getroot()
    replace_all(svg_root, replacements)
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
    try:
        return teams_replacements[t]
    except KeyError:
        return t


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
    if t1.startswith("NHB"):
        t1 += "-"+normalize_level(match.level)
    else:
        t2 += "-" + normalize_level(match.level)

    base = "match"+str(id)+"-"
    return {
        base+"team1": t1,
        base+"team2": t2,
        base+"time": match.time + ' - ' + match.place,
    }

def generate_posts(dates_to_matches):
    for date, matches in dates_to_matches.items():
        other_matches = []
        for match in matches:
            rs = {"date": convert_date(date)}
            if match.level.startswith("H1"):
                rs |= replacements_from_hd_match(match,1)
                update_template('match_day_h1', date.isoformat(), rs)
                update_template('results_h1', date.isoformat(), rs, False)
            elif match.level.startswith("D3"):
                rs |= replacements_from_hd_match(match,1)
                update_template('match_day_d3', date.isoformat(), rs)
                update_template('results_d3', date.isoformat(), rs, False)
            else:
                other_matches.append(match)

        if other_matches:
            rs = {"date": convert_date(date)}
            md_template = "match_day_"+str(len(other_matches))
            r_template = "match_day_"+str(len(other_matches))
            other_matches.sort(key=lambda m: m.time)
            for i, match in enumerate(other_matches, start=1):
                rs |= replacements_from_match(match, i)
            update_template(md_template, date.isoformat(), rs)
            update_template(r_template, date.isoformat(), rs, False)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(svg_output_folder), exist_ok=True)
    os.makedirs(os.path.dirname(png_output_folder), exist_ok=True)

    matches = parse_calendar(sys.argv[1])
    generate_posts(matches)


