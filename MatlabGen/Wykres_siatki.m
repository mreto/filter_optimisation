function Wykres_siatki(mesh,j)

  tri = mesh.t(:,1:3);
  x   = 1000*mesh.p(:,1);
  y   = 1000*mesh.p(:,2);
  
  if ~exist('linespec')
    linespec = 'r';
  end
  figure(j)
  triplot(tri,x,y,linespec);
  
end