python : Traceback (most recent call
 last):
所在位置 行:1 字符: 1
+ python -c "import re; f=open(r'e:\
ideaProjects\agent\Noosphere\README 
...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSp 
   ecified: (Traceback (most recen  
  t call last)::String) [], Remot   
 eException
    + FullyQualifiedErrorId : Nativ 
   eCommandError
 
  File "<string>", line 1, in <modul
e>
    import re; f=open(r'e:\ideaProje
cts\agent\Noosphere\README.md','r',e
ncoding='utf-8-sig'); lines=f.readli
nes(); f.close(); headers=[(i+1,l.st
rip()[:90]) for i,l in enumerate(lin
es) if l.strip().startswith('#')]; [
print(f'{n}: {h}') for n,h in header
s]
                                    
                                    
                                    
                                    
                                    
                                    
~~~~~^^^^^^^^^^^^^
UnicodeEncodeError: 'gbk' codec can'
t encode character '\U0001f30c' in p
osition 7: illegal multibyte sequenc
e
