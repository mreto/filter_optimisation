function [Ep]=Porzadkuj_wektor_pobudzenia(V1w,V2w,mesh)
  
    %kolejne elementy wektor�w pobudze�
    l1=1;
    l2=1;
    %rozmiar wektora pobudze� x2 we wrotach 1 i 2
    Ep=sparse(size(mesh.p,1),2);
    
    %porz�dkowanie wektora pobudze�, na poszczeg�lne w�z�y siatki
    
    for i=1:size(V1w,1)
      Ep(V1w(i,2),1)=V1w(i,1);
      Ep(V2w(i,2),2)=V2w(i,1);
    end

end