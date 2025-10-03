@bot.on(events.NewMessage(pattern='/tasks'))
async def handle_tasks_command(event):
    """Mevcut görevleri liste halinde göster"""
    try:
        user_id = str(event.sender_id)
        sender = await event.get_sender()
        
        logger.info(f"Kullanıcı görevleri istedi: {user_id}")
        
        # Backend API'den aktif görevleri al
        tasks = []
        try:
            # Örnek: REST API'den görevleri al
            if api_client:
                tasks = await api_client.get_tasks()
            # Veya görevleri direkt task_manager üzerinden al
            else:
                # Not: Bu kısım task_manager yapısına göre ayarlanmalıdır
                # Burada örnek bir görev listesi sunuyoruz
                tasks = [
                    {
                        "id": "join_channel",
                        "title": "Kanala Katıl",
                        "description": "Resmi telegram kanalımıza katıl",
                        "reward": {"xp": 10, "token": 1}
                    },
                    {
                        "id": "send_message",
                        "title": "Mesaj Gönder",
                        "description": "Gruba mesaj gönder",
                        "reward": {"xp": 5, "token": 1}
                    },
                    {
                        "id": "emoji_reaction",
                        "title": "Emoji Tepkisi Ver",
                        "description": "Duyuru mesajına emoji tepkisi ver",
                        "reward": {"xp": 5, "token": 1}
                    },
                    {
                        "id": "group_join_message",
                        "title": "Gruba Katıl ve Mesaj Gönder",
                        "description": "Yeni grubumuza katıl ve kendini tanıt",
                        "reward": {"xp": 20, "token": 3}
                    }
                ]
        except Exception as e:
            logger.error(f"Görevler alınırken hata: {e}")
            await event.respond("⚠️ Görevler alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
            return
        
        if not tasks:
            await event.respond("📋 Şu anda mevcut görev bulunmamaktadır.")
            return
        
        # Görevlerden inline butonlar oluştur
        from telethon import Button
        
        # Her görev için bir buton oluştur
        task_buttons = []
        for task in tasks:
            # Görev bilgisi ve ödül
            reward_text = f"{task.get('reward', {}).get('xp', 0)} XP + {task.get('reward', {}).get('token', 0)} $VIPX"
            
            # Her satırda bir görev butonu
            task_buttons.append([
                Button.inline(
                    f"🎯 {task['title']} ({reward_text})",
                    data=f"task_info_{task['id']}"
                )
            ])
            
        # Mesajı gönder
        await event.respond(
            f"📋 **Mevcut Görevler**\n\n"
            f"Aşağıdaki görevlerden birini seçerek detayları görebilir ve görevi başlatabilirsiniz:",
            buttons=task_buttons
        )
        
    except Exception as e:
        logger.error(f"/tasks komutunda hata: {e}")
        await event.respond("⚠️ Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

@bot.on(events.CallbackQuery(pattern=r"task_info_(.+)"))
async def handle_task_info(event):
    """Görev detaylarını göster ve başlatma seçeneği sun"""
    try:
        user_id = str(event.sender_id)
        task_id = event.data.decode('utf-8').split('_')[-1]
        
        logger.info(f"Kullanıcı görev detayı istedi: {user_id}, görev: {task_id}")
        
        # İlgili görevi bul (backend API'den veya yerel cache'den)
        task = None
        try:
            # Örnek: REST API'den görevi al
            if api_client:
                task = await api_client.get_task(task_id)
            # Veya görevi direkt task_manager üzerinden al
            else:
                # Örnek veri
                tasks = {
                    "join_channel": {
                        "id": "join_channel",
                        "title": "Kanala Katıl",
                        "description": "Resmi telegram kanalımıza katılarak ödül kazanın. Katıldıktan sonra bot otomatik olarak tamamlandığını tespit edecektir.",
                        "type": "channel_join_v2",
                        "reward": {"xp": 10, "token": 1},
                        "params": {
                            "channel_id": "@onlyvips_channel"
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "send_message": {
                        "id": "send_message",
                        "title": "Mesaj Gönder",
                        "description": "Topluluğumuza destek olmak için gruba mesaj gönderin. Mesajınız en az 10 karakter uzunluğunda olmalıdır.",
                        "type": "message_send",
                        "reward": {"xp": 5, "token": 1},
                        "params": {
                            "chat_id": "@onlyvips_group",
                            "min_length": 10
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "emoji_reaction": {
                        "id": "emoji_reaction",
                        "title": "Emoji Tepkisi Ver",
                        "description": "Kanalımızdaki son duyuru mesajına 👍 emoji tepkisi verin.",
                        "type": "emoji_reaction",
                        "reward": {"xp": 5, "token": 1},
                        "params": {
                            "target_chat_id": "@onlyvips_channel",
                            "target_message_id": 456,
                            "target_emoji": "👍"
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "group_join_message": {
                        "id": "group_join_message",
                        "title": "Gruba Katıl ve Mesaj Gönder",
                        "description": "Yeni topluluk grubumuza katılın ve kendinizi tanıtan bir mesaj gönderin. Mesajınız en az 30 karakter uzunluğunda olmalıdır.",
                        "type": "group_join_message",
                        "reward": {"xp": 20, "token": 3},
                        "params": {
                            "group_username": "@onlyvips_community",
                            "min_length": 30
                        },
                        "duration": "7 gün",
                        "difficulty": "Orta"
                    }
                }
                task = tasks.get(task_id)
        except Exception as e:
            logger.error(f"Görev detayı alınırken hata: {e}")
            await event.answer("Görev detayları alınamadı", alert=True)
            return
        
        if not task:
            await event.answer("Bu görev artık mevcut değil", alert=True)
            return
        
        # Görev bilgilerini hazırla
        reward_text = f"{task.get('reward', {}).get('xp', 0)} XP + {task.get('reward', {}).get('token', 0)} $VIPX"
        difficulty = task.get('difficulty', 'Normal')
        duration = task.get('duration', '24 saat')
        
        # Butonları hazırla
        from telethon import Button
        buttons = [
            [Button.inline("🚀 Görevi Başlat", data=f"start_task_{task_id}")],
            [Button.inline("◀️ Geri Dön", data="back_to_tasks")]
        ]
        
        # Mesajı gönder
        await event.edit(
            f"🎯 **{task['title']}**\n\n"
            f"📝 **Açıklama:** {task['description']}\n\n"
            f"💰 **Ödül:** {reward_text}\n"
            f"⏱️ **Süre:** {duration}\n"
            f"📊 **Zorluk:** {difficulty}\n\n"
            f"Görevi başlatmak için aşağıdaki butona tıklayın:",
            buttons=buttons
        )
        
    except Exception as e:
        logger.error(f"Görev detayları gösterilirken hata: {e}")
        await event.answer("Bir hata oluştu", alert=True)

@bot.on(events.CallbackQuery(pattern=r"back_to_tasks"))
async def handle_back_to_tasks(event):
    """Görev listesine geri dön"""
    try:
        # /tasks komutunu yeniden çağır
        message = await event.get_message()
        await message.delete()
        
        # Yeni bir /tasks komutu oluştur
        new_event = events.NewMessage.Event(
            message=message,
            pattern='/tasks',
            out=False,
            forwards=False
        )
        new_event._sender = await event.get_sender()
        
        # /tasks komut işleyicisini çağır
        await handle_tasks_command(new_event)
        
    except Exception as e:
        logger.error(f"Görev listesine dönülürken hata: {e}")
        await event.answer("Görev listesi yüklenemedi", alert=True)

@bot.on(events.CallbackQuery(pattern=r"start_task_(.+)"))
async def handle_start_task(event):
    """Görevi başlat"""
    try:
        user_id = str(event.sender_id)
        task_id = event.data.decode('utf-8').split('_')[-1]
        
        logger.info(f"Kullanıcı görev başlatıyor: {user_id}, görev: {task_id}")
        
        # Kullanıcının günlük limit aşımını kontrol et
        from utils.task_logger import TaskLogger
        task_logger = TaskLogger()
        
        # İlgili görev tipini bul
        task_type = None
        try:
            # Örnek: görev tipini bul
            if api_client:
                task = await api_client.get_task(task_id)
                task_type = task.get("type")
            else:
                # Örnek veri
                task_types = {
                    "join_channel": "channel_join_v2",
                    "send_message": "message_send",
                    "emoji_reaction": "emoji_reaction",
                    "group_join_message": "group_join_message"
                }
                task_type = task_types.get(task_id)
        except Exception as e:
            logger.error(f"Görev tipi belirlenirken hata: {e}")
            await event.answer("Görev başlatılamadı", alert=True)
            return
        
        if not task_type:
            await event.answer("Görev tipi belirlenemedi", alert=True)
            return
        
        # Günlük limit kontrolü
        if not await task_logger.check_daily_limit(user_id, task_type):
            await event.answer("Bu görevi bugün zaten tamamladınız. Lütfen yarın tekrar deneyin.", alert=True)
            return
        
        # Soğuma süresi kontrolü
        # Not: Gerçek bir spam kontrolü için TaskManager veya benzeri bir sistem kullanılmalıdır
        # Burada basit bir örnek gösteriyoruz
        
        # Görevi başlat
        try:
            # Görev parametrelerini al
            if api_client:
                task = await api_client.get_task(task_id)
                params = task.get("params", {})
            else:
                # Örnek veri
                params_map = {
                    "join_channel": {"channel_id": "@onlyvips_channel"},
                    "send_message": {"chat_id": "@onlyvips_group", "min_length": 10},
                    "emoji_reaction": {"target_chat_id": "@onlyvips_channel", "target_message_id": 456, "target_emoji": "👍"},
                    "group_join_message": {"group_username": "@onlyvips_community", "min_length": 30}
                }
                params = params_map.get(task_id, {})
            
            # Görevi ata ve başlat
            # Not: Gerçek bir sistemde task_manager kullanılmalıdır
            success = True
            
            if success:
                # Günlük limit sayacını artır
                await task_logger.increment_daily_limit(user_id, task_type)
                
                # Başarılı mesajını göster
                from telethon import Button
                
                # Görev tipine göre özel mesajlar
                task_instructions = {
                    "channel_join_v2": f"Kanala katılmak için: [Kanala Git](https://t.me/{params.get('channel_id', '').lstrip('@')})",
                    "message_send": f"Mesaj göndermek için: [Gruba Git](https://t.me/{params.get('chat_id', '').lstrip('@')})",
                    "emoji_reaction": f"Emoji tepkisi vermek için: [Mesaja Git](https://t.me/{params.get('target_chat_id', '').lstrip('@')}/{params.get('target_message_id')})",
                    "group_join_message": f"Gruba katılmak için: [Gruba Git](https://t.me/{params.get('group_username', '').lstrip('@')})"
                }
                
                instruction = task_instructions.get(task_type, "Görev başlatıldı. Devam etmek için talimatları takip edin.")
                
                await event.edit(
                    f"🚀 **Görev Başlatıldı**\n\n"
                    f"**Görev:** {task_id}\n\n"
                    f"📝 **Yapılacaklar:**\n{instruction}\n\n"
                    f"Görev otomatik olarak kontrol edilecektir. Tamamlandığında size bildirim gönderilecektir.",
                    buttons=[Button.inline("◀️ Görevlere Dön", data="back_to_tasks")],
                    link_preview=True
                )
                
                logger.info(f"Görev başarıyla başlatıldı: {user_id}, görev: {task_id}")
            else:
                await event.answer("Görev başlatılamadı. Lütfen daha sonra tekrar deneyin.", alert=True)
                
        except Exception as e:
            logger.error(f"Görev başlatılırken hata: {e}")
            await event.answer("Görev başlatılırken bir hata oluştu", alert=True)
        
    except Exception as e:
        logger.error(f"Görev başlatma işleminde hata: {e}")
        await event.answer("Bir hata oluştu", alert=True)

@bot.on(events.NewMessage(pattern='/myprogress'))
async def handle_myprogress_command(event):
    """Kullanıcının görev ilerlemesini göster"""
    try:
        user_id = str(event.sender_id)
        sender = await event.get_sender()
        
        logger.info(f"Kullanıcı ilerleme durumunu istedi: {user_id}")
        
        # Kullanıcı ilerleme durumunu al
        from utils.task_logger import TaskLogger
        task_logger = TaskLogger()
        
        progress = await task_logger.get_user_progress(user_id)
        
        # İlerleme mesajını oluştur
        total_tasks = progress.get("completed_tasks", 0)
        xp = progress.get("xp", 0)
        token = progress.get("token", 0)
        last_week = progress.get("last_week_tasks", 0)
        
        # Görev tiplerine göre dağılım
        task_types = progress.get("task_types", {})
        type_text = ""
        
        if task_types:
            type_text = "\n**Görev Tiplerine Göre:**\n"
            for task_type, count in task_types.items():
                # Task tipini daha okunabilir hale getir
                readable_type = {
                    "channel_join_v2": "Kanala Katılma",
                    "message_send": "Mesaj Gönderme",
                    "button_click": "Buton Tıklama",
                    "start_link": "Start Link",
                    "voting": "Oylama",
                    "schedule_post": "Zamanlanmış Mesaj",
                    "comment": "Yorum Yapma",
                    "follow_account": "Hesap Takip",
                    "emoji_reaction": "Emoji Tepkisi",
                    "group_join_message": "Gruba Katılma ve Mesaj"
                }.get(task_type, task_type)
                
                type_text += f"- {readable_type}: {count} görev\n"
        
        # Seviye hesapla (basit bir formül)
        level = 1 + (xp // 100)  # Her 100 XP'de bir seviye
        next_level_xp = (level * 100)
        xp_progress = xp % 100  # Bir sonraki seviyeye kalan XP
        
        # Seviye ilerleme çubuğu
        progress_bar = "▓" * (xp_progress // 10) + "░" * (10 - (xp_progress // 10))
        
        # Mesajı gönder
        from telethon import Button
        
        await event.respond(
            f"📊 **İlerleme Durumunuz**\n\n"
            f"👤 **Kullanıcı:** {sender.first_name}\n"
            f"⭐ **Seviye:** {level}\n"
            f"📈 **XP:** {xp}/{next_level_xp} [{xp_progress}%]\n"
            f"[{progress_bar}]\n\n"
            f"💰 **$VIPX Token:** {token}\n"
            f"🎯 **Tamamlanan Görevler:** {total_tasks}\n"
            f"📅 **Son 7 Gün:** {last_week} görev\n"
            f"{type_text}\n\n"
            f"Daha fazla görev tamamlayarak seviyenizi yükseltebilir ve ödüller kazanabilirsiniz!",
            buttons=[Button.inline("📋 Görevleri Görüntüle", data="back_to_tasks")]
        )
        
    except Exception as e:
        logger.error(f"/myprogress komutunda hata: {e}")
        await event.respond("⚠️ İlerleme durumunuz alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.") 