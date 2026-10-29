from pathlib import Path
import json,hashlib
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
src=Path('C:/Users/123/Desktop/Wei_Feng_Academic_CV_Draft.docx');d=Document(src)
blocks=[]
heads=['CONFERENCE PAPERS AND ACADEMIC PRESENTATIONS','ACADEMIC ACTIVITIES','SELECTED SCHOLARSHIPS, AWARDS AND HONORS']
for el in d.element.body:
 if el.tag==qn('w:p'):
  p=Paragraph(el,d);t=p.text
  if t: blocks.append({'kind':'heading' if p.style.name=='Section Head' or t in heads else 'entry' if p.style.name=='Entry Head' else 'text','en':t})
 elif el.tag==qn('w:tbl'):
  t=Table(el,d);blocks.append({'kind':'date','en':' | '.join(c.text for c in t.rows[0].cells)})
zh='''冯薇
建筑学博士研究生 | 面向建成遗产的人工智能
东南大学建筑学院 建筑运算与应用实验室（Lab AAA）\n邮箱：wei.feng@seu.edu.cn | 电话：(+86)18851667823
研究方向
建成遗产保护与更新；图表示学习；历史聚落时空分析；知识引导的学习与可解释知识发现。
教育经历
建筑学直博 | 2024年9月至今
东南大学建筑学院
• 预计毕业时间：2029年6月。
• 2024年入选校级“至善卓越”直博生计划。
建筑学学士 | 2019年9月—2024年6月
东南大学建筑学院
• 本科绩点：3.98 / 4.8；排名：4 / 87（前5%）。
工科本科基础培养 | 2018年9月—2019年9月
东南大学吴健雄学院
• 本科绩点：4.16 / 4.8；排名：2 / 142（前1.5%）。
研究经历
中国传统村落全国尺度时空图研究
东南大学 | 在研
• 参与构建覆盖8,155个传统村落的全国性研究数据集，整合建筑轮廓、道路与2015、2020、2025年多时相遥感证据。
• 将建筑与道路构型表示为异构图；采用孪生关系图神经网络（R-GCN）与256维村落嵌入，学习地理、文化与产业语境下的成对相似性。
• 比较人工构建的形态与类型描述指标和学习得到的图表示，分析可见形态相似性与关系相似性的一致与分歧。
• 历史观测是对2025年可观测空间要素的回溯，不构成对早期已消失要素的完整清单。
历史性城镇景观时空图谱与决策支持
东南大学同心城市更新教育基金 | 研究团队，2026—2027
• 研究多源时空演变图谱，以及用于保护与城市更新的知识引导证据。
行为导向的城市形态优化
研究成果发表于ISUF 2025
• 合作研究基于运筹算法的混合居住社区空间优化，结合几何约束与关系空间构型。
科研项目
历史性城镇景观多源时空演变图谱与智能决策研究
项目负责人 | 东南大学同心城市更新教育基金 | 2026年1月—2027年12月（在研）
数据驱动的历史地段多尺度层级保护更新方法研究
研究参与者 | 国家自然科学基金面上项目 | 项目编号52178008 | 2022年1月—2025年12月
高密度城市街区儿童友好性评价模型与优化策略
研究参与者 | 江苏省大学生创新训练计划 | 2021年1月—2022年12月
会议论文与学术报告
2026年10月 “Identifying Relational Similarities in Living Historic Settlements: A Spatio-Temporal Graph Study of 8,155 Chinese Traditional Villages.” ICOMOS大会（ICOMOS GA 2026）。
2025年6月 “Behavior-oriented Urban Spatial Form Optimization Driven by Operations Research Algorithms: A Case Study of a Mixed-Use Residential Community in Nanjing.” 国际城市形态研讨会（ISUF 2025），口头报告，意大利。
2026年10月 “From Morphology to Relations: A Spatio-Temporal Graph Study of 8,155 Chinese Traditional Villages.” 新加坡国立大学建筑系，Knowledge Modelling for Built Heritage & Conservation，受邀研究报告，10月23日。
学术活动
2026年6月 DigitalFUTURES 2026暑期工作营助教 | “Dream Weaving: Knowledge Decoding and AI Reconstruction of Historic Districts”
2024年2—7月 建筑学学术交流 | 意大利都灵理工大学
• 课程：城市规划；建造历史；后碳建筑的节能设计。
奖学金 奖励与荣誉
2025年 研究生学业奖学金二等奖 | 东南大学
2024年 直博生至善卓越奖学金 | 东南大学
2022年 本科生国家奖学金 | 中国
2022年 程泰宁奖励基金 | 东南大学建筑设计与理论研究中心
2019、2020年 唐仲英奖学金 | 东南大学
2019年 三好学生 | 东南大学
研究方法与技术经验
异构图构建；关系图神经网络（R-GCN）；孪生相似性学习；图嵌入学习；成对评估；空间形态描述指标比较；卫星影像建筑与道路提取；多时相空间分析。
语言能力
英语：大学英语六级676 / 710；大学英语四级599 / 710。'''.splitlines()
# Embedded line break in contact is one paragraph.
zh[2:4]=[zh[2]+'\n'+zh[3]]
assert len(zh)==len(blocks),(len(zh),len(blocks))
for b,t in zip(blocks,zh):b['zh']=t
for en,cn in [('SELECTED PUBLICATIONS','代表性论文'),('INTELLECTUAL PROPERTY','知识产权'),('SELECTED DESIGN AND DEVELOPMENT PROJECTS','代表性设计与开发项目'),('TEACHING EXPERIENCE','教学经历'),('ACADEMIC SERVICES','学术服务')]:
 blocks.extend([{'kind':'heading','en':en,'zh':cn},{'kind':'blank','en':'','zh':''}])
Path('cv-content.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
Path('tmp').mkdir(exist_ok=True)
Path('tmp/artifact.md').write_text(f'Reference: {src}\nSHA256: {hashlib.sha256(src.read_bytes()).hexdigest()}\nA4 portrait, margins top 0.56 in and left 0.68 in. Lato 9pt body, 19pt name, blue 9.5pt uppercase section headings, dates aligned right in borderless tables. Preserve source Word formatting. Add empty union sections. Render unavailable: LibreOffice not installed.\n',encoding='utf-8')
