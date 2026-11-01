"""Deterministic source -> candidate graph -> explicit engineering hypothesis."""
from pathlib import Path
import hashlib
import json
import math
import unicodedata

DATA = Path(__file__).resolve().parent / 'data'
FIELDS = {'id','source_verse','source_text','concept','relationship_type','related_concept',
          'interpretation','source_reference','confidence','verification_status',
          'schema_version','epistemic_level','rule_id'}
RELATIONS = {'bağlam','eylem','koşul','süreç'}

class ValidationError(ValueError):
    pass

def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',',':')).encode('utf-8')

def comparison_text(text):
    # Only an auxiliary comparison/search view. Original verse string is never rewritten.
    return ''.join(c for c in unicodedata.normalize('NFKD',text)
                   if not unicodedata.category(c).startswith('M') and c not in 'ـ ۞').replace('ٱ','ا')

def read_json(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValidationError('duplicate JSON key')
            d[k]=v
        return d
    def invalid(x): raise ValidationError('nonfinite JSON')
    return json.loads(Path(path).read_text(encoding='utf8'),object_pairs_hook=unique,parse_constant=invalid)

class Core:
    def __init__(self, data=DATA):
        self.data=Path(data)
        lock=read_json(self.data/'source_lock.json')
        expected={'verses.json','comparison.json','rules.json','sources.json','tafsir_index.json','hypothesis.json','TANZIL_LICENSE.txt'}
        if set(lock['files']) != expected: raise ValidationError('source lock coverage')
        for name,digest in lock['files'].items():
            path=self.data/name
            if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                raise ValidationError('source integrity: '+name)
        self.verses=read_json(self.data/'verses.json')['verses']
        if [v['id'] for v in self.verses] != [f'48:{i}' for i in range(1,30)]: raise ValidationError('verse sequence')
        if any(set(v)!={'id','text'} or not isinstance(v['text'],str) or not v['text'] for v in self.verses): raise ValidationError('verse shape')
        self.by_verse={v['id']:v['text'] for v in self.verses}
        other=read_json(self.data/'comparison.json')['verses']
        if len(other)!=29 or any(a['id']!=b['id'] or comparison_text(a['text'])!=comparison_text(b['text']) for a,b in zip(self.verses,other)):
            raise ValidationError('second-channel comparison')
        self.sources=read_json(self.data/'sources.json')
        self.source_ids={s['id'] for s in self.sources}
        self.tafsir={s['id']:s for s in read_json(self.data/'tafsir_index.json')}
        self.rules=read_json(self.data/'rules.json')
        if len({r['id'] for r in self.rules})!=len(self.rules): raise ValidationError('duplicate rule')
        self.hypothesis=read_json(self.data/'hypothesis.json')
        self.records=self.extract()

    def extract(self):
        out=[]
        for r in self.rules:
            verse=r['source_verse']
            if verse not in self.by_verse: raise ValidationError('rule verse outside scope')
            text=self.by_verse[verse]
            if not r['needle'] or comparison_text(r['needle']) not in comparison_text(text):
                raise ValidationError('rule has no text evidence: '+r['id'])
            rec={'schema_version':'1.0','id':'F01-'+r['id'],'rule_id':r['id'],
                 'source_verse':verse,'source_text':text,'concept':r['concept'],
                 'relationship_type':r['relationship_type'],'related_concept':r['related_concept'],
                 'interpretation':r['interpretation'],
                 'source_reference':['tanzil-uthmani-1.1','diyanet-tefsir-48',f"tafsir:{r['tafsir_id']}"],
                 'confidence':0.5,'verification_status':'PENDING_HUMAN_REVIEW','epistemic_level':'K3'}
            self.validate_record(rec)
            out.append(rec)
        return sorted(out,key=lambda x:x['id'])

    def validate_record(self, rec):
        if not isinstance(rec,dict) or set(rec)!=FIELDS: raise ValidationError('record fields')
        for key in FIELDS-{'confidence','source_reference'}:
            if not isinstance(rec[key],str) or not rec[key].strip(): raise ValidationError('record text: '+key)
        if rec['schema_version']!='1.0' or rec['epistemic_level']!='K3': raise ValidationError('record version/level')
        if rec['verification_status']!='PENDING_HUMAN_REVIEW': raise ValidationError('human review required; no promotion endpoint')
        if rec['source_verse'] not in self.by_verse or rec['source_text']!=self.by_verse[rec['source_verse']]: raise ValidationError('verse identity/text')
        if rec['relationship_type'] not in RELATIONS: raise ValidationError('relationship')
        c=rec['confidence']
        if type(c) not in (float,int) or not math.isfinite(c) or not 0<=c<=1: raise ValidationError('confidence')
        refs=rec['source_reference']
        if not isinstance(refs,list) or len(refs)!=3 or len(set(str(x) for x in refs))!=3 or any(not isinstance(x,str) for x in refs): raise ValidationError('references')
        if not {'tanzil-uthmani-1.1','diyanet-tefsir-48'}.issubset(refs): raise ValidationError('required references')
        tf=[x[7:] for x in refs if x.startswith('tafsir:')]
        if len(tf)!=1 or tf[0] not in self.tafsir: raise ValidationError('tafsir identity')
        t=self.tafsir[tf[0]];v=int(rec['source_verse'].split(':')[1])
        if not int(t['first'].split(':')[1])<=v<=int(t['last'].split(':')[1]): raise ValidationError('tafsir range')
        rule=next((r for r in self.rules if r['id']==rec['rule_id']),None)
        if rule is None or rec['id']!='F01-'+rule['id'] or rec['source_verse']!=rule['source_verse']: raise ValidationError('rule identity')
        for key in ['concept','related_concept','relationship_type','interpretation']:
            if rec[key]!=rule[key]: raise ValidationError('unsupported interpretation')
        return True

    def graph(self, concept=None):
        edges=[{'id':r['id'],'from':r['concept'],'to':r['related_concept'],'type':r['relationship_type'],
                'record_id':r['id'],'source_verse':r['source_verse'],'status':r['verification_status']} for r in self.records
               if concept is None or concept in (r['concept'],r['related_concept'])]
        return {'nodes':sorted({e[k] for e in edges for k in ('from','to')}),'edges':edges,'semantics':'CANDIDATE_RELATIONS_NOT_VERIFIED_TAFSIR'}

    def hypotheses(self):
        matched={r['rule_id']:r for r in self.records}
        needed=self.hypothesis['source_records']
        if not all(x in matched for x in needed):return []
        value=json.loads(canonical(self.hypothesis))
        value['generated_by']='source-linked hypothesis template v1.0, human-authored K4 analogy'
        value['grounding_records']=[matched[x]['id'] for x in needed]
        value['interpretation_status']='PENDING_HUMAN_REVIEW'
        return [value]

    def models(self):
        # Human-authored K4 structure linked to a candidate, not semantic entailment from scripture.
        if not self.hypotheses():return []
        return [{'id':'P01','epistemic_level':'K4','status':'EXPERIMENTAL',
                 'source_record':'F01-R07','process':['aday adımı seç','bağımlılık ve kaynak kontrolü','gölge sıralama','sonucu ölç'],
                 'condition':'bağımlılıklar tamam ve bütçe yeterli','action':'uygun işleri kısa süreye göre sırala',
                 'result':'tamamlanan işlerin hedef değerini ölç','hypothesis_id':'H01',
                 'boundary':'Mühendislik analojisi; K1/K2 açıklaması veya dinî hüküm değildir.'}]

    def export(self):
        return {'tanzil_notice':(self.data/'TANZIL_LICENSE.txt').read_text(encoding='utf8'),'schema_version':'1.0','scope':'48:1-29','verses':self.verses,'sources':self.sources,
                'records':self.records,'graph':self.graph(),'models':self.models(),'hypotheses':self.hypotheses(),
                'interpretation_acceptance':'HOLD_HUMAN_REVIEW','real_benefit_acceptance':'NOT_TESTED',
                'confidence_meaning':'0.5 fixed candidate-priority marker, not calibrated probability or religious certainty'}
