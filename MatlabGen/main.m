clear
clc
close all

Load_Points();
load Tomasz_Mesh

siatka_plot=0;

%wyznaczenie macierzy C i T
[C,T] = Macierz_C_T(mesh);

if siatka_plot
    Wykres_siatki(mesh,1);
end

%wspolczynnik odbicia
[S,f,S11,S21] = Wyznacz_macierz_S(C,T,mesh,siatka_plot);
