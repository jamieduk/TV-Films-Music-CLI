
#!/usr/bin/env python3
# (c) J~Net 2026

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from collections import defaultdict

# ============================================================
# MEDIA LOCATIONS
# ============================================================

# FILM LOCATIONS
films_path="/run/media/jay/59D1-02E4/Vids/Films"
more_films_path="/run/media/jay/SSD/Torrent-Downloads/More-Films"

# TV LOCATIONS
tv_path="/run/media/jay/59D1-02E4/Vids/TV-SHOWS"
more_tv_path="/run/media/jay/SSD/Torrent-Downloads/More-TV"

# MUSIC LOCATIONS
music_path="/run/media/jay/59D1-02E4/Vids/Music_Vids"

# xxx VIDEO LOCATIONS
xxx_videos_path="/run/media/jay/59D1-02E4/Vids/xxx"

# ============================================================
# SETTINGS
# ============================================================

VIDEO_EXTENSIONS={
    ".mp4",".mkv",".avi",".mov",".m4v",
    ".wmv",".webm",".mpg",".mpeg",".ts"
}

AUDIO_EXTENSIONS={
    ".mp3",".flac",".wav",".m4a",".aac",
    ".ogg",".opus",".wma",".alac",".aiff"
}

xxx_VIDEO_EXTENSIONS=VIDEO_EXTENSIONS

VIDEO_ROOTS=[
    films_path,
    more_films_path,
    tv_path,
    more_tv_path,
    xxx_videos_path
]

AUDIO_ROOTS=[
    music_path
]

# Terminal colours
GREEN="\033[92m"
DARK_GREEN="\033[32m"
WHITE="\033[97m"
YELLOW="\033[93m"
RED="\033[91m"
CYAN="\033[96m"
RESET="\033[0m"
BOLD="\033[1m"

# ============================================================
# TERMINAL FUNCTIONS
# ============================================================

def clear_screen():
    os.system("clear" if os.name=="posix" else "cls")


def banner():
    print(f"{GREEN}{BOLD}")
    print("╔══════════════════════════════════════════════╗")
    print("║             🎬 J~NET MEDIA PLAYER            ║")
    print("║              MPV MEDIA MANAGER               ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"{RESET}")


def status(message,colour=GREEN):
    print(f"\n{colour}➜ {message}{RESET}")


def pause():
    input(f"\n{DARK_GREEN}Press ENTER to continue...{RESET}")


def menu(title,options):
    clear_screen()
    banner()

    print(f"{CYAN}{BOLD}📂 {title}{RESET}\n")

    for number,label in enumerate(options,1):
        print(f"{GREEN}{number:>3}.{RESET} {WHITE}{label}{RESET}")

    print(f"\n{YELLOW}  0. ↩ Back / Exit{RESET}")

    while True:
        choice=input(f"\n{GREEN}Select an option: {WHITE}").strip()
        print(RESET,end="")

        if choice=="0":
            return 0

        if choice.isdigit() and 1<=int(choice)<=len(options):
            return int(choice)

        status("Invalid selection. Try again.",RED)


def natural_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)",str(value))
    ]


def clean_name(path):
    return path.stem


def unique_files(files):
    seen=set()
    result=[]

    for file in files:
        key=str(file.resolve())

        if key not in seen:
            seen.add(key)
            result.append(file)

    return sorted(result,key=lambda p:natural_key(p.name))


# ============================================================
# MEDIA SCANNER
# ============================================================

def scan_locations(locations,extensions):
    results=[]

    for location in locations:
        root=Path(location).expanduser()

        if not root.exists():
            continue

        if not root.is_dir():
            continue

        try:
            for current,dirs,files in os.walk(root,followlinks=False):
                dirs.sort(key=natural_key)

                for filename in files:
                    file=Path(current)/filename

                    if file.suffix.lower() in extensions:
                        results.append(file)

        except PermissionError:
            continue

    return unique_files(results)


def get_films():
    return scan_locations(
        [films_path,more_films_path],
        VIDEO_EXTENSIONS
    )


def get_tv():
    return scan_locations(
        [tv_path,more_tv_path],
        VIDEO_EXTENSIONS
    )


def get_music():
    return scan_locations(
        [music_path],
        AUDIO_EXTENSIONS
    )


def get_xxx_videos():
    return scan_locations(
        [xxx_videos_path],
        xxx_VIDEO_EXTENSIONS
    )


def get_all_media():
    return unique_files(
        get_films()+
        get_tv()+
        get_music()+
        get_xxx_videos()
    )


# ============================================================
# FILE DISPLAY
# ============================================================

def display_file(file,index):
    print(
        f"{GREEN}{index:>3}.{RESET} "
        f"{WHITE}{file.name}{RESET}"
    )


def display_files(files):
    for index,file in enumerate(files,1):
        display_file(file,index)


def file_location(file):
    return str(file.parent)


def print_file_details(file):
    print(f"{CYAN}📁 {file.parent}{RESET}")
    print(f"{WHITE}🎬 {file.name}{RESET}")


# ============================================================
# MPV PLAYBACK
# ============================================================

def play_files(files):
    files=unique_files([Path(f) for f in files])

    if not files:
        status("No files to play.",RED)
        pause()
        return

    mpv=shutil.which("mpv")

    if not mpv:
        status("MPV is not installed or cannot be found.",RED)
        print(f"{YELLOW}Install with: sudo apt install -y mpv{RESET}")
        pause()
        return

    clear_screen()
    banner()

    print(f"{GREEN}▶ Starting MPV...{RESET}")
    print(f"{CYAN}📁 Files queued: {len(files)}{RESET}\n")

    for file in files:
        print(f"{DARK_GREEN}  • {file.name}{RESET}")

    command=[
        mpv,
        "--save-position-on-quit",
        "--resume-playback",
        "--",
        *[str(file) for file in files]
    ]

    try:
        subprocess.run(command,check=False)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        status(f"MPV error: {error}",RED)

    status("Playback finished.")


def playback_menu(files,title="Playback"):
    files=unique_files(files)

    if not files:
        status("No media files found.",RED)
        pause()
        return

    while True:
        options=[
            f"▶ Play selected file ({len(files)} available)",
            "⏩ Play from selected file onwards",
            "▶▶ Play all files",
            "📋 List files"
        ]

        choice=menu(title,options)

        if choice==0:
            return

        if choice==1:
            selected=select_file(files,title)

            if selected is not None:
                play_files([files[selected]])

        elif choice==2:
            selected=select_file(files,title)

            if selected is not None:
                play_files(files[selected:])

        elif choice==3:
            play_files(files)

        elif choice==4:
            clear_screen()
            banner()
            display_files(files)
            pause()


def select_file(files,title="Select File"):
    if not files:
        return None

    while True:
        clear_screen()
        banner()

        print(f"{CYAN}📋 {title}{RESET}\n")
        display_files(files)
        print(f"\n{YELLOW}  0. ↩ Back{RESET}")

        choice=input(f"\n{GREEN}Select file: {WHITE}").strip()
        print(RESET,end="")

        if choice=="0":
            return None

        if choice.isdigit() and 1<=int(choice)<=len(files):
            return int(choice)-1

        status("Invalid selection.",RED)


# ============================================================
# FILM COLLECTIONS
# ============================================================

def film_collection_key(file):
    name=file.stem.lower()

    # Remove release year
    name=re.sub(r"[\s._-]*\(?\b(19|20)\d{2}\)?$", "",name)

    # Remove sequel numbering and common Roman numeral suffixes
    name=re.sub(
        r"[\s._-]+(?:part[\s._-]*)?(?:\d+|ii|iii|iv|v|vi|vii|viii|ix|x)$",
        "",
        name,
        flags=re.IGNORECASE
    )

    name=re.sub(r"[^a-z0-9]+"," ",name).strip()

    return name or file.stem.lower()


def build_film_collections(files):
    groups=defaultdict(list)

    for file in files:
        # Films in their own subfolder are grouped by folder.
        # Films directly inside a root are grouped by title.
        key=str(file.parent).lower()

        if file.parent.name.lower() in [
            "films","mor-films"
        ]:
            key="collection:"+film_collection_key(file)

        groups[key].append(file)

    collections=[]

    for key,items in groups.items():
        items=unique_files(items)

        if len(items)>1:
            name=(
                Path(key.replace("collection:","")).name
                if not key.startswith("collection:")
                else items[0].stem
            )

            if key.startswith("collection:"):
                name=film_collection_key(items[0]).title()

            collections.append((name,items))

        else:
            collections.append((items[0].stem,items))

    return sorted(
        collections,
        key=lambda item:natural_key(item[0])
    )


def films_menu():
    films=get_films()

    while True:
        collections=build_film_collections(films)

        options=[
            f"🎬 {name} ({len(items)} films)"
            for name,items in collections
        ]

        options.insert(0,f"📋 List all films ({len(films)})")

        choice=menu("FILM LIBRARY",options)

        if choice==0:
            return

        if choice==1:
            playback_menu(films,"ALL FILMS")
            continue

        name,items=collections[choice-2]

        playback_menu(items,f"🎬 {name}")


# ============================================================
# TV SHOWS AND SEASONS
# ============================================================

def get_season_info(file,roots):
    for root_string in roots:
        root=Path(root_string).expanduser()

        try:
            relative=file.relative_to(root)
        except ValueError:
            continue

        parts=list(relative.parts)

        season_index=None
        season_name="Unsorted"

        for index,part in enumerate(parts[:-1]):
            match=re.search(
                r"(?:season|series|s)[\s._-]*(\d+)",
                part,
                re.IGNORECASE
            )

            if match:
                season_index=index
                season_name=f"Season {int(match.group(1)):02d}"
                break

        if season_index is not None:
            show_name=parts[season_index-1] if season_index>0 else root.name
        elif len(parts)>1:
            show_name=parts[0]
        else:
            show_name="Unsorted TV"

        return show_name,season_name

    return "Unsorted TV","Unsorted"


def build_tv_library(files):
    shows=defaultdict(lambda:defaultdict(list))

    for file in files:
        show,season=get_season_info(
            file,[tv_path,more_tv_path]
        )

        shows[show][season].append(file)

    return shows


def tv_menu():
    files=get_tv()
    shows=build_tv_library(files)

    while True:
        options=[
            f"📺 {show} ({sum(len(v) for v in seasons.values())} episodes)"
            for show,seasons in sorted(
                shows.items(),
                key=lambda item:natural_key(item[0])
            )
        ]

        options.insert(0,f"📋 List all TV episodes ({len(files)})")

        choice=menu("TV SHOW LIBRARY",options)

        if choice==0:
            return

        if choice==1:
            playback_menu(files,"ALL TV EPISODES")
            continue

        show_name=list(sorted(
            shows.keys(),key=natural_key
        ))[choice-2]

        seasons=shows[show_name]

        while True:
            season_names=sorted(
                seasons.keys(),
                key=natural_key
            )

            season_options=[
                f"📁 {season} ({len(seasons[season])} episodes)"
                for season in season_names
            ]

            season_choice=menu(
                f"📺 {show_name} - SEASONS",
                season_options
            )

            if season_choice==0:
                break

            season_name=season_names[season_choice-1]
            episodes=unique_files(seasons[season_name])

            playback_menu(
                episodes,
                f"{show_name} - {season_name}"
            )


# ============================================================
# MUSIC AND xxx VIDEOS
# ============================================================

def folder_groups(files):
    groups=defaultdict(list)

    for file in files:
        groups[file.parent.name].append(file)

    return sorted(
        groups.items(),
        key=lambda item:natural_key(item[0])
    )


def browse_grouped_media(files,title,group_label):
    while True:
        groups=folder_groups(files)

        options=[
            f"{group_label} {name} ({len(items)} files)"
            for name,items in groups
        ]

        options.insert(0,f"📋 Play/list all ({len(files)} files)")

        choice=menu(title,options)

        if choice==0:
            return

        if choice==1:
            playback_menu(files,f"ALL {title}")
            continue

        name,items=groups[choice-2]

        playback_menu(items,name)


def music_menu():
    browse_grouped_media(
        get_music(),
        "MUSIC LIBRARY",
        "🎵"
    )


def xxx_videos_menu():
    browse_grouped_media(
        get_xxx_videos(),
        "XXX VIDEO LIBRARY",
        "🎞️"
    )


# ============================================================
# SEARCH
# ============================================================

def search_media():
    while True:
        clear_screen()
        banner()

        print(f"{CYAN}🔎 MEDIA SEARCH{RESET}\n")

        query=input(
            f"{GREEN}Enter film, episode, song or artist name: {WHITE}"
        ).strip()

        print(RESET,end="")

        if not query:
            return

        all_files=get_all_media()

        matches=[
            file for file in all_files
            if query.casefold() in file.name.casefold()
            or query.casefold() in str(file.parent).casefold()
        ]

        matches=unique_files(matches)

        clear_screen()
        banner()

        print(f"{CYAN}🔎 SEARCH RESULTS: {query}{RESET}\n")

        if not matches:
            status("No matching media found.",YELLOW)
            pause()
            return

        print(f"{GREEN}Found {len(matches)} matching files:\n{RESET}")

        for index,file in enumerate(matches,1):
            extension=file.suffix.lower()

            if extension in AUDIO_EXTENSIONS:
                emoji="🎵"
            else:
                emoji="🎬"

            print(
                f"{GREEN}{index:>3}.{RESET} "
                f"{emoji} {WHITE}{file.name}{RESET}"
            )
            print(f"     {DARK_GREEN}{file.parent}{RESET}")

        print(f"\n{YELLOW}  0. ↩ Back{RESET}")

        choice=input(
            f"\n{GREEN}Select a file: {WHITE}"
        ).strip()

        print(RESET,end="")

        if choice=="0":
            return

        if choice.isdigit() and 1<=int(choice)<=len(matches):
            selected=int(choice)-1

            playback_menu(
                matches[selected:],
                "SEARCH RESULTS"
            )
        else:
            status("Invalid selection.",RED)
            pause()


# ============================================================
# ALL MEDIA BROWSER
# ============================================================

def all_media_menu():
    while True:
        files=get_all_media()

        options=[
            f"📋 All media ({len(files)} files)",
            f"🎬 Films ({len(get_films())})",
            f"📺 TV shows ({len(get_tv())})",
            f"🎵 Music ({len(get_music())})",
            f"🎞️ xxx videos ({len(get_xxx_videos())})"
        ]

        choice=menu("ALL MEDIA",options)

        if choice==0:
            return

        if choice==1:
            playback_menu(files,"ALL MEDIA")
        elif choice==2:
            films_menu()
        elif choice==3:
            tv_menu()
        elif choice==4:
            music_menu()
        elif choice==5:
            xxx_videos_menu()


# ============================================================
# LIBRARY INFORMATION
# ============================================================

def library_info():
    while True:
        clear_screen()
        banner()

        print(f"{CYAN}📊 MEDIA LIBRARY INFORMATION{RESET}\n")

        categories=[
            ("🎬 Films",[films_path,more_films_path],VIDEO_EXTENSIONS),
            ("📺 TV Shows",[tv_path,more_tv_path],VIDEO_EXTENSIONS),
            ("🎵 Music",[music_path],AUDIO_EXTENSIONS),
            ("🎞️ XXX Videos",[xxx_videos_path],xxx_VIDEO_EXTENSIONS)
        ]

        for name,locations,extensions in categories:
            count=len(scan_locations(locations,extensions))
            print(f"{GREEN}{name}: {WHITE}{count} files{RESET}")

        print(f"\n{CYAN}📂 CONFIGURED LOCATIONS{RESET}\n")

        for name,locations in [
            ("Films",[films_path,more_films_path]),
            ("TV",[tv_path,more_tv_path]),
            ("Music",[music_path]),
            ("XXX Videos",[xxx_videos_path])
        ]:
            print(f"{YELLOW}{name}:{RESET}")

            for location in locations:
                exists=Path(location).is_dir()
                indicator="✓" if exists else "✗"
                colour=GREEN if exists else RED

                print(f"  {colour}{indicator} {location}{RESET}")

        print(f"\n{YELLOW}0. ↩ Back{RESET}")

        if input(f"\n{GREEN}Press ENTER to return...{RESET}")=="":
            return


# ============================================================
# MAIN MENU
# ============================================================

def main():
    if not shutil.which("mpv"):
        clear_screen()
        banner()

        status("MPV is not installed.",RED)
        print(f"\n{YELLOW}Install MPV using:{RESET}")
        print(f"{GREEN}sudo apt install -y mpv{RESET}")
        return

    while True:
        options=[
            "🔎 Search Media",
            "🎬 Browse All Films",
            "📺 Browse TV Shows",
            "🎵 Browse Music",
            "🎞️ Browse XXX Videos",
            "📂 Browse All Media",
            "📊 Library Information",
            "🔄 Refresh / Rescan Library"
        ]

        choice=menu("MAIN MENU",options)

        if choice==0:
            clear_screen()
            print(f"{GREEN}👋 Thanks for using J~Net Media Player!{RESET}")
            break

        elif choice==1:
            search_media()

        elif choice==2:
            films_menu()

        elif choice==3:
            tv_menu()

        elif choice==4:
            music_menu()

        elif choice==5:
            xxx_videos_menu()

        elif choice==6:
            all_media_menu()

        elif choice==7:
            library_info()

        elif choice==8:
            status("Library will be rescanned on the next operation.")


if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{GREEN}👋 Exiting J~Net Media Player.{RESET}")
        sys.exit(0)

