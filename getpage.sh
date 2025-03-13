#!/bin/bash


function remove_bak_dir() {
  local _dir="$1"
  
  if [[ -n "$(ls "$_dir" || exit )" ]]; then
    rm -r "$_dir.bak"
    mv "$_dir" "$_dir.bak"
  fi
}

function remove_bak_file() {
  local _file="$1"
  
  if [[ -n "$(cat "$_file" || exit )"  ]]; then
    rm  "$_file.bak"
    mv "$_file" "$_file.bak"
  fi
}

remove_bak_dir "pics"
remove_bak_dir "contrasted"
remove_bak_dir "cleared"

remove_bak_file "Viewer"
remove_bak_file "result.pdf"


wget --load-cookies "$HOME/Downloads/cookies.txt"  "https://weblibranet.linguanet.ru/ProtectedView2022/App/Viewer"


PIC_DIR="pics"

all_pages="$(cat Viewer | grep "Всего страниц в файле" | cut -f2 -d "/" | cut -f1 -d "<")"
regid="$(cat Viewer | grep "/ProtectedView2022/App/GetPage" | awk -F "{" '{print $3}' | awk -F "}" '{print $1}')"
token="$(cat Viewer | grep "var token = " | cut -f2 -d '"')"

mkdir "$PIC_DIR"

# i=1
# while ((i <= all_pages)); do
#     echo "$i"
#     wget --load-cookies "$HOME/Downloads/cookies.txt"  -O "$PIC_DIR/page_$i.png"  "https://weblibranet.linguanet.ru/ProtectedView2022/App/GetPage/$i?token=$token&width=800&height=1131&resid=$regid"  
#     i="$(echo "$i + 1" | bc)"
# done

touch urls.txt
echo '' > urls.txt

seq 1 "$all_pages" | xargs -I {} echo "{}" >> urls.txt

## Download using xargs (adjust -P for number of parallel processes)
xargs -P 10 -I {} wget --load-cookies "$HOME/Downloads/cookies.txt" -O "$PIC_DIR/page_{}.png" "https://weblibranet.linguanet.ru/ProtectedView2022/App/GetPage/{}?token=$token&width=800&height=1131&resid=$regid"  < urls.txt

exit
venv/bin/python3 main.py


