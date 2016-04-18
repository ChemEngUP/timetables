#!/usr/bin/env sed -f
#!/bin/sed -f
s,Rek/Comp,Comp,g
s,Regsgebou/Law,Law,g
s,Ing/Eng,Eng,g
s,Teologie/Theology,Theol.,g
s,Louwsaal/Louw,Louw,g
s,GW/HSB,HSB,g
s,GW/HB,HSB,g
s,Wisk/Maths,Maths,g
s,Noordsaal/North,North,g
s,Suidsaal/South,South,g
s,Oudit/Audit,Audit,g
s,Mullersaal/Muller,Muller,g
s,Roossaal/Roos,Roos,g
s,Te Watersaal/Te,Te,g
s,Elek/Elec,Elec,g
s,Anneks/Annex,Annex,g
s,Groot Chemie/Large,Large,g
s,VD Bijlsaal/VD,VD,g
s,Theronsaal/Theron,Theron,g
s,EB/EMB,EMB,g
s,Build Sc/Boukunde,Boukunde,g
s,Raadpl.*/.*Consult [Dd]ept,TBA,g
s,Raadpleeg [Dd]ept/.*Consult [Dd]ept,TBA,g
s/TBA,.*TBA/TBA/g
s,Geografie/Geography,Geography,g
s,Min Wet/Science,Min Sci,g
s,Netwerke/Networks,Networks,g
s,Eeufees/Centenary,Centenary,g
s,JJ Theronsaal/JJ Theron hall,JJ Theron hall,g
s/&amp;/and/g
s/ *& */ and /g
s/'//g
s,Monday,Ma/Mo,g
s,Tuesday,Di/Tu,g
s,Wednesday,Wo/We,g
s,Thursday,Do/Th,g
s,Friday,Vr/Fr,g
s,K1/Q1,Q1,g
s,K2/Q2,Q2,g
s,K3/Q3,Q3,g
s,K4/Q4,Q4,g
s,J/Y,Y,g
s/[KQ]\([0-9]\) [EI]NG/Q\1/g
