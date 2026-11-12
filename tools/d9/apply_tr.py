import json,re
def apply(s,D):
    d=json.load(open(D+'tr_dict.json',encoding='utf-8'))
    rx=json.load(open(D+'tr_rx.json',encoding='utf-8'))
    # 1. регэкспы (защищаем плейсхолдерами от словаря)
    store=[]
    for old,new in sorted(rx,key=lambda p:-len(p[0])):
        if old==new: continue
        if old in s:
            store.append(new)
            s=s.replace(old,'\x00RX%d\x00'%(len(store)-1))
    # 2. словарь: самые длинные первыми, границы по буквам
    keys=sorted(d,key=lambda k:-len(k))
    L='А-Яа-яЁёІіЇїЄєҐґ'
    pat=re.compile('(?<![%s])(?:%s)(?![%s])'%(L,'|'.join(re.escape(k) for k in keys),L))
    s=pat.sub(lambda m:d[m.group(0)],s)
    s=re.sub('\x00RX(\\d+)\x00',lambda m:store[int(m.group(1))],s)
    for old,new in FIX:
        assert old in s,old
        s=s.replace(old,new)
    return s

FIX=[
('💰 и "+S.fz','💰 і "+S.fz'),
('"горить 🔥":"нет")','"горить 🔥":"немає")'),
('"виставлено 👀":"нет")','"виставлено 👀":"немає")'),
('"готова 🥣":"нет")','"готова 🥣":"немає")'),
('"доглянутий 🐎":"нет")','"доглянутий 🐎":"немає")'),
('"да":"нет"','"так":"ні"'),
(': уже в тебе',': вже в тебе'),
('" из "','" з "'),
('Перстень уже на','Перстень вже на'),
('обоз уже пройшов','обоз вже пройшов'),
('(r.tl?" и "+r.tl','(r.tl?" і "+r.tl'),
('у Чобіт — и энергия вырастет.','у Чобіт — і енергія зросте.'),
('<b>Еда</b> и 💧','<b>Їжа</b> і 💧'),
('бій уже скінчився','бій вже скінчився'),
('n:"Усы"','n:"Вуса"'),
('L=[["Ты",','L=[["Ти",'),
('{t:"Бой",x:','{t:"Бій",x:'),
('aria-label="Фон"','aria-label="Тло"'),
('backdrop:"Фон"','backdrop:"Тло"'),
('h+"ч "+(m<10?"0":"")+m+"м"','h+"г "+(m<10?"0":"")+m+"хв"'),
('h+" ч "+m+" мин":m>0?m+" мин "+c+" с":c+" с"','h+" г "+m+" хв":m>0?m+" хв "+c+" с":c+" с"'),
('return m+" мин";var h=Math.floor(m/60);return h+" ч "+(m%60?(m%60)+" мин":"")','return m+" хв";var h=Math.floor(m/60);return h+" г "+(m%60?(m%60)+" хв":"")'),
("<small>ур. '","<small>рів. '"),
]
