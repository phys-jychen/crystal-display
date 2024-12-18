#! /bin/bash

#source ~/conda.env

particle="e-"
energy=0.5
threshold=0.1

source_path="/cefs/higgs/chenjiyuan/crystal2024/Data/Processed_Data_Storage/2024_06_CERN_T9/Crystal_Module/FERS-5200_CERN_Configuration/Reconstruction"
dir="20240707_Elec0.5GeV_HG34_1_LG49_24_TimingHG250_Shaping87.5ns_HoldDelay400ns_wTrigger_wCooling_1.5mmCollimator_OldTBFile"
outputdir="/cefs/higgs/chenjiyuan/crystal2024/figs-display/${dir}"
mkdir -p ${outputdir}

filename="${source_path}/${dir}/RecoEnergy_Thr${threshold}.root"
event_index=9
output="EventDisplay_${particle}_${energy}GeV_Thr${threshold}_evt${event_index}.pdf"
#show=0

title="${energy} GeV "
if [ $particle = "e-" ]; then
    title+='$e^-$'
elif [ $particle = "mu-" ]; then
    title+='$\mu^-$'
elif [ $particle = "pi-" ]; then
    title+='$\pi^-$'
elif [ $particle = "e+" ]; then
    title+='$e^+$'
elif [ $particle = "mu+" ]; then
    title+='$\mu^+$'
elif [ $particle = "pi+" ]; then
    title+='$\pi^+$'
fi

python /cefs/higgs/chenjiyuan/crystal2024/EventDisplay/display.py -f=$filename -i="$title" -e=$event_index -r=$threshold -d=$outputdir -o="$output"
