function [V1,V2,kc1,kc2] = Wektor_pobudzenia_ALL(mesh)
  %http://www.personal.psu.edu/alm24/undergrad/FEMHelmholtz.pdf
  Z0=120*pi;
  for point=1:2
  if (point==1)
    poz=mesh.p_enter;
  elseif (point==2)
    poz=mesh.p_exit;
  end
  
  const=size(poz,1);
  Len=(max(poz(:,2))-min(poz(:,2)))/(const+1);
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  P1=eye(const)*4;

  P2=eye(const+1);
  P2(:,const+1)=[];
  P2(1,:)=[];

  P3=eye(const+1);
  P3(const+1,:)=[];
  P3(:,1)=[];

  P=P1+P2+P3;
  T=P*Len/6;
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  H1=eye(const)*2;

  H2=eye(const+1);
  H2(:,const+1)=[];
  H2(1,:)=[];
  H2=-H2;

  H3=eye(const+1);
  H3(const+1,:)=[];
  H3(:,1)=[];
  H3=-H3;

  H=H1+H2+H3;
  C=H/Len;
  
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  [V,lambda] = eigs(C, T,1,'SM');
  kc=sqrt(lambda);
  fc=kc*3*10^8/(2*pi);
  %normalizacja wektora pobudzenia
  
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  if (point==1)
    V1(:,1)=T*V*Z0;  
    V1w=mesh.t_enter;
    kc1=kc;
  elseif (point==2)
    V2(:,1)=T*V*Z0;  
    V1w=mesh.t_exit;
    kc2=kc;
  end
  [~,index]=sort(mesh.p(V1w,2),'descend');
  V1w=V1w(index);
  if (point==1)
    V1(:,2)=V1w(1:size(V1w,1),1);
  elseif (point==2)
    V2(:,2)=V1w(1:size(V1w,1),1);
  end
  
  end
end