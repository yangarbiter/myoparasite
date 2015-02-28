#!/bin/sh

mkdir -p images
cd images
for i in left right; do
	for j in thumb index-finger middle-finger ring-finger little-finger; do
		wget "https://git.gnome.org/browse/gnome-control-center/plain/panels/user-accounts/data/icons/${i}-${j}.svg"
	done
done
