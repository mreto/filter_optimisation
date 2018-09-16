function [C,T] = Macierz_C_T(mesh)

    C=sparse(size(mesh.p,1),size(mesh.p,1));
    T=sparse(size(mesh.p,1),size(mesh.p,1));


    p=mesh.p;
    t=mesh.t;

    for i=1:size(mesh.t,1)
        %wspolrzedne wierzcholkow
          Ex=[p(t(i,1),1)  ;p(t(i,2),1)   ;p(t(i,3),1)];
          Ey=[p(t(i,1),2)  ;p(t(i,2),2)   ;p(t(i,3),2)];

          P=[Ey(2)-Ey(3);Ey(3)-Ey(1);Ey(1)-Ey(2)];
          Q=[Ex(3)-Ex(2);Ex(1)-Ex(3);Ex(2)-Ex(1)];
          A=0.5*(P(2)*Q(3)-P(3)*Q(2));
          if(A<0)
              keyboard
              A=abs(A);
              disp(num2str(i));
          end
          for K=1:3
              for L=1:3
                  C(t(i,K),t(i,L))=C(t(i,K),t(i,L))+0.25/A*(P(K)*P(L)+Q(K)*Q(L));
                  if (K==L)
                      T(t(i,K),t(i,L))=T(t(i,K),t(i,L))+A/6;
                  else
                      T(t(i,K),t(i,L))=T(t(i,K),t(i,L))+A/12;
                  end   
              end
          end
    end
end
