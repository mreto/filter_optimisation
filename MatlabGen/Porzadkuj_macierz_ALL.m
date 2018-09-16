function [ Ct,Tt,Bp,mesh ] = Porzadkuj_macierz_ALL( Ct,Tt,Bp,mesh,siatka_plot)

    %wyznaczony zosta³ wektor przes³on Ww okreœlaj¹cy które wêz³y nale¿¹ do PEC
    %nastêpnie z macierzy Ct, Tt oraz wektora pobudzeñ redukujê elementy PEC
    
    W=mesh.t_boundary;
    if siatka_plot
        Wykres_siatki(mesh,2);
        hold on;
        scatter(mesh.p(W,1)*1000,mesh.p(W,2)*1000,'filled','k')
        title('Wycinam PEC')
    end
    
    Ct(:,W)=[];
    Ct(W,:)=[];
    Tt(:,W)=[];
    Tt(W,:)=[];
    Bp(W,:)=[];
    mesh.p(W,:)=[];
    
end