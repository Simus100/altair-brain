"""Verify only the staged public files, without using installed local brains."""
import json,os,pathlib,shutil,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[1]
dest=pathlib.Path(tempfile.mkdtemp(prefix='altair-public-verification-'))
for rel in subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0'):
 if rel and (root/rel).is_file():
  out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,out)
subprocess.run(['git','init','-q'],cwd=dest,check=True)
subprocess.run(['git','add','-A'],cwd=dest,check=True,capture_output=True)
env={k:v for k,v in os.environ.items() if not k.startswith('ALTAIR_')}
env['PYTHONIOENCODING']='utf-8'
steps=[('distribution',['tools/check_distribution.py']),('virgin-build',['tools/rebuild_all.py']),('virgin-tests',['-m','pytest','tests/','-q','-p','no:cacheprovider']),('adopt-training',['tools/brain_new.py','--nome','ci-training','--aree','notes','--training','aion']),('training-build',['tools/rebuild_all.py']),('training-tests',['-m','pytest','tests/','-q','-p','no:cacheprovider'])]
results=[]
log=root/'output/verification';log.mkdir(parents=True,exist_ok=True)
for name,args in steps:
 p=subprocess.run([sys.executable,*args],cwd=dest,env=env,capture_output=True,text=True,encoding='utf8',timeout=240)
 (log/f'{name}.log').write_text(p.stdout+p.stderr,encoding='utf8')
 record={'step':name,'exit_code':p.returncode,'summary':(p.stdout+p.stderr)[-700:]};results.append(record)
 print(json.dumps(record),flush=True)
 (log/'results.json').write_text(json.dumps(results,indent=2),encoding='utf8')
 if p.returncode: raise SystemExit(f'Failed {name}; see {log}')
print('Clean public distribution verified:',dest)
