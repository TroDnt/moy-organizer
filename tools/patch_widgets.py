#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
p=Path(__import__('os').environ['PROJECT_DIR'])
res=p/'app/src/main/res'
# Widget picker labels and resizing metadata
info={
'tasks_widget_info.xml':('Задачи — список дел','horizontal|vertical','180dp','120dp'),
'calendar_widget_info.xml':('Календарь — сегодня и смена','horizontal|vertical','160dp','100dp'),
'shift_widget_info.xml':('График смен — день и ночь','horizontal|vertical','180dp','120dp')}
strings=res/'values/strings.xml'
root=ET.parse(strings).getroot()
for key,val in [('widget_tasks_label','Задачи — список дел'),('widget_calendar_label','Календарь — сегодня и смена'),('widget_shift_label','График смен — день и ночь')]:
 if not any(x.attrib.get('name')==key for x in root.findall('string')):
  ET.SubElement(root,'string',name=key).text=val
ET.indent(root,space='    ')
ET.ElementTree(root).write(strings,encoding='utf-8',xml_declaration=True)
for fn,(label,resize,w,h) in info.items():
 f=res/'xml'/fn
 tree=ET.parse(f); node=tree.getroot()
 node.set('{http://schemas.android.com/apk/res/android}label','@string/'+({'tasks_widget_info.xml':'widget_tasks_label','calendar_widget_info.xml':'widget_calendar_label','shift_widget_info.xml':'widget_shift_label'}[fn]))
 node.set('{http://schemas.android.com/apk/res/android}resizeMode',resize)
 node.set('{http://schemas.android.com/apk/res/android}minResizeWidth',w)
 node.set('{http://schemas.android.com/apk/res/android}minResizeHeight',h)
 ET.indent(tree,space='    ')
 tree.write(f,encoding='utf-8',xml_declaration=True)
# Make task rows and status clearer
layout=res/'layout/widget_tasks.xml'
s=layout.read_text()
s=s.replace('android:textSize="13sp"','android:textSize="15sp" android:maxLines="2" android:ellipsize="end"')
s=s.replace('android:textSize="11sp" android:paddingBottom="4dp"','android:textSize="12sp" android:paddingBottom="6dp"')
s=s.replace('android:paddingVertical="4dp"','android:paddingVertical="6dp"')
layout.write_text(s)
# Bright adaptive launcher icon vector
drawable=res/'drawable'
drawable.mkdir(exist_ok=True)
(drawable/'ic_launcher_fg.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
 <path android:fillColor="#FFFFFFFF" android:pathData="M28,24h52v60h-52z"/>
 <path android:fillColor="#FF8B5CF6" android:pathData="M22,18h52a6,6 0,0 1,6 6v58a6,6 0,0 1,-6 6h-52a6,6 0,0 1,-6 -6v-58a6,6 0, 0 6,-6z"/>
 <path android:fillColor="#FF1E293B" android:pathData="M27,30h48v50h-48z"/>
 <path android:fillColor="#FF38BDF8" android:pathData="M34,18h34v8h-34z"/>
 <path android:fillColor="#FFFFFFFF" android:pathData="M37,43l6,6 11,-13 5,4 -16,18 -11,-11z"/>
 <path android:fillColor="#FFFFD166" android:pathData="M37,67l6,6 11,-13 5,4 -16,18 -11,-11z"/>
</vector>''')
mipmap=res/'mipmap-anydpi-v26'; mipmap.mkdir(exist_ok=True)
(mipmap/'ic_launcher.xml').write_text('''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
 <background android:drawable="@color/launcher_bg"/>
 <foreground android:drawable="@drawable/ic_launcher_fg"/>
</adaptive-icon>''')
colors=res/'values/colors.xml'
cr=ET.Element('resources')
ET.SubElement(cr,'color',name='launcher_bg').text='#FF7C3AED'
colors.write_text(ET.tostring(cr,encoding='unicode'))
manifest=p/'app/src/main/AndroidManifest.xml'
ms=manifest.read_text().replace('<application android:theme=', '<application android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher" android:theme=')
manifest.write_text(ms)
print('Widget labels, resize metadata, text readability and launcher icon patched')

# Improve completion visibility and make the tasks widget title open the app.
provider=p/'app/src/main/java/com/myorganizer/app/TasksWidgetProvider.kt'
ps=provider.read_text()
ps=ps.replace('views.setTextViewText(textIds[index], task.optString("title"))', '''views.setTextViewText(textIds[index], if (done) "✓  " + task.optString("title") else task.optString("title"))
                    views.setTextColor(textIds[index], if (done) 0xFF6B7280.toInt() else 0xFFFFFFFF.toInt())''')
ps=ps.replace('manager.updateAppWidget(widgetId, views)', '''val openApp = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val openPending = PendingIntent.getActivity(context, 7000 + widgetId, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            views.setOnClickPendingIntent(R.id.widget_title, openPending)
            views.setOnClickPendingIntent(R.id.widget_subtitle, openPending)
            manager.updateAppWidget(widgetId, views)''')
provider.write_text(ps)
print('Task widget completion styling and title/subtitle app navigation patched')
