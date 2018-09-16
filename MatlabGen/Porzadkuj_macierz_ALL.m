function [ Ct,Tt,Bp,mesh ] = Porzadkuj_macierz_ALL( Ct,Tt,Bp,mesh,siatka_plot)

    %wyznaczony zosta� wektor przes�on Ww okre�laj�cy kt�re w�z�y nale�� do PEC
    %nast�pnie z macierzy Ct, Tt oraz wektora pobudze� redukuj� elementy PEC
    
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