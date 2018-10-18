function main(id)
if(exist("id", "var") == 0)
  id = 'no_thread';
end
Load_Points(id);
## load_string = 
load(['Tomasz_Mesh_' id])
siatka_plot=0;

%wyznaczenie macierzy C i T
[C,T] = Macierz_C_T(mesh);

if siatka_plot
    Wykres_siatki(mesh,1);
end

%wspolczynnik odbicia
[S,f,S11,S21] = Wyznacz_macierz_S(C,T,mesh,siatka_plot, id);
end
