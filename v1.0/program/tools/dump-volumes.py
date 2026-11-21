import FreeCAD as A,csv
d=A.openDocument('cad/Bavuso-V1.0-adventure.FCStd')
with open('program/data/run/cad-volumes.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['name','vol_cm3','area_cm2'])
    for o in d.Objects:
        if o.TypeId!='Part::Feature' or not o.InList:continue
        s=o.Shape;w.writerow([o.Name,round(sum(abs(x.Volume) for x in s.Solids)/1000,2),round(s.Area/100,1)])
