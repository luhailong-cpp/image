import production as p
import sys
p.T=p.ROOT/'r08_c12'
p.ORIGIN=(45056,28672)
p.WEST=p.ROOT/'r08_c11/output/r08_c11.png'
def status():
 p.savej(p.T/'progress.json',{'tile':'r08_c12','globalRect':[45056,28672,4096,4096],'updatedAtUtc':p.now(),'nativePatchesSaved':len(list((p.T/'native').glob('r??_c??.png'))),'nativePatchesRequired':16,'countsAsCompleteTile':False,'formalAccepted':False,'phase':'native_expansion_in_progress'})
p.status=status
if __name__=='__main__':
 if sys.argv[1]=='prepare':p.prepare(int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
 elif sys.argv[1]=='record':p.record(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='status':status()
