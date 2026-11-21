from pathlib import Path
import os
p=Path(os.environ["PROJECT_DIR"])
src=p/"app/src/main/java/com/myorganizer/app"
(src/"ShiftAlarm.kt").write_text("""package com.myorganizer.app
import android.app.*
import android.content.*
import android.os.Build
import androidx.core.app.NotificationCompat
import org.json.*
import java.time.*
object ShiftAlarm {
 private const val action="com.myorganizer.app.SHIFT_WAKE"
 private const val channel="shift_wake_alarm"
 private fun pref(c:Context)=c.getSharedPreferences("my_organizer_data",0)
 fun enabled(c:Context)=pref(c).getBoolean("shift_alarm_enabled",false)
 fun time(c:Context,k:String)=pref(c).getString("shift_alarm_$k",when(k){"day"->"06:30";"night"->"14:00";else->"09:00"})?:"09:00"
 fun setTime(c:Context,k:String,v:String){pref(c).edit().putString("shift_alarm_$k",v).apply();schedule(c)}
 fun setEnabled(c:Context,v:Boolean){pref(c).edit().putBoolean("shift_alarm_enabled",v).apply();if(v)schedule(c)else cancel(c)}
 private fun pending(c:Context)=PendingIntent.getBroadcast(c,9821,Intent(c,ShiftAlarmReceiver::class.java).setAction(action),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
 fun cancel(c:Context){(c.getSystemService(Context.ALARM_SERVICE) as AlarmManager).cancel(pending(c))}
 fun schedule(c:Context){
  if(!enabled(c)){cancel(c);return}
  val p=pref(c);val today=LocalDate.now();val o=runCatching{JSONObject(p.getString("shifts","{}"))}.getOrDefault(JSONObject());val cy=runCatching{JSONObject(p.getString("shift_cycle","{}"))}.getOrDefault(JSONObject());val arr=runCatching{JSONArray(cy.optString("pattern","[]"))}.getOrDefault(JSONArray());val anchor=runCatching{LocalDate.parse(cy.optString("anchorDate",today.toString()))}.getOrDefault(today)
  for(n in 0..14){val date=today.plusDays(n.toLong());val type=o.optString(date.toString(),if(arr.length()>0)arr.optString(Math.floorMod(java.time.temporal.ChronoUnit.DAYS.between(anchor,date),arr.length().toLong()).toInt())else "");if(type.isBlank())continue
   val key=when(type.lowercase()){"day","день","дневная"->"day";"night","ночь","ночная"->"night";else->"off"};val t=runCatching{LocalTime.parse(time(c,key))}.getOrDefault(LocalTime.of(9,0));val at=date.atTime(t).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();if(at>System.currentTimeMillis()+1000){val a=c.getSystemService(Context.ALARM_SERVICE) as AlarmManager;if(Build.VERSION.SDK_INT>=31&&!a.canScheduleExactAlarms())a.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,pending(c))else if(Build.VERSION.SDK_INT>=23)a.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,pending(c))else a.setExact(AlarmManager.RTC_WAKEUP,at,pending(c));return}
  }
 }
 fun notify(c:Context){val nm=c.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager;if(Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(NotificationChannel(channel,"Будильник по сменам",NotificationManager.IMPORTANCE_HIGH));val open=PendingIntent.getActivity(c,9822,Intent(c,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP;putExtra("open_section","Будильник")},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);nm.notify(9821,NotificationCompat.Builder(c,channel).setSmallIcon(android.R.drawable.ic_lock_idle_alarm).setContentTitle("Пора вставать").setContentText("Будильник по графику смен").setPriority(NotificationCompat.PRIORITY_HIGH).setContentIntent(open).setAutoCancel(true).build())}
}
class ShiftAlarmReceiver:BroadcastReceiver(){override fun onReceive(c:Context,i:Intent){when(i.action){Intent.ACTION_BOOT_COMPLETED,Intent.ACTION_TIME_CHANGED,Intent.ACTION_TIMEZONE_CHANGED->ShiftAlarm.schedule(c);"com.myorganizer.app.SHIFT_WAKE"->{if(ShiftAlarm.enabled(c)){ShiftAlarm.notify(c);ShiftAlarm.schedule(c)}}}}}
""")
main=src/"MainActivity.kt"; s=main.read_text()
s=s.replace('"Напоминания") } ?: "Главная")','"Напоминания", "Будильник") } ?: "Главная")')
s=s.replace('"Напоминания" to Icons.Default.Notifications).forEach','"Напоминания" to Icons.Default.Notifications, "Будильник" to Icons.Default.Alarm).forEach')
s=s.replace('"Напоминания" -> RemindersScreen(context, reminders)','"Напоминания" -> RemindersScreen(context, reminders)\n                    "Будильник" -> ShiftAlarmScreen(context)')
if "fun ShiftAlarmScreen(context: Context)" not in s:
 s += """\n@Composable
fun ShiftAlarmScreen(context:Context){
 var active by remember{mutableStateOf(ShiftAlarm.enabled(context))}
 var day by remember{mutableStateOf(ShiftAlarm.time(context,"day"))}
 var night by remember{mutableStateOf(ShiftAlarm.time(context,"night"))}
 var off by remember{mutableStateOf(ShiftAlarm.time(context,"off"))}
 Text("Будильник по сменам",color=Color.White,style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
 Text("Время автоматически выбирается по графику календаря.",color=muted)
 Row(verticalAlignment=Alignment.CenterVertically){Text("Включить будильник",color=Color.White,modifier=Modifier.weight(1f));Switch(active,{active=it;ShiftAlarm.setEnabled(context,it)})}
 @Composable fun pick(label:String,v:String,k:String,update:(String)->Unit){Card(colors=CardDefaults.cardColors(containerColor=panel),modifier=Modifier.fillMaxWidth()){Row(Modifier.padding(12.dp),verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(label,color=Color.White);Text(v,color=accent,style=MaterialTheme.typography.headlineSmall)};Button(onClick={val a=v.split(":");android.app.TimePickerDialog(context,{_,h,m->val x="%02d:%02d".format(h,m);update(x);ShiftAlarm.setTime(context,k,x)},a[0].toInt(),a[1].toInt(),true).show()}){Text("Изменить")}}};Spacer(Modifier.height(8.dp))}
 pick("☀️ Дневная смена",day,"day"){day=it};pick("🌙 Ночная смена",night,"night"){night=it};pick("🛌 Выходной",off,"off"){off=it}
 Text("Учитывает цикл смен и ручные изменения в календаре. Если график не задан, будильник не назначается.",color=muted)
}
"""
main.write_text(s)
manifest=p/"app/src/main/AndroidManifest.xml"; m=manifest.read_text()
rec='''        <receiver android:name=".ShiftAlarmReceiver" android:enabled="true" android:exported="false"><intent-filter><action android:name="android.intent.action.BOOT_COMPLETED"/><action android:name="android.intent.action.TIME_SET"/><action android:name="android.intent.action.TIMEZONE_CHANGED"/></intent-filter></receiver>
        <receiver android:name=".ShiftAlarmReceiver" android:enabled="true" android:exported="false"><intent-filter><action android:name="com.myorganizer.app.SHIFT_WAKE"/></intent-filter></receiver>
'''
if "ShiftAlarmReceiver" not in m:m=m.replace('        <receiver android:name=".ReminderReceiver"',rec+'        <receiver android:name=".ReminderReceiver"',1)
manifest.write_text(m)
print("Shift alarm patched")
