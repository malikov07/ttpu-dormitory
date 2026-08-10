"""All UI text strings in 3 languages: uz, en, ru."""

TEXTS = {
    "uz": {
        "welcome": (
            "🏛 <b>TTPU Yotoqxona Ariza Boti</b>\n\n"
            "Assalomu alaykum! Iltimos, tilni tanlang:"
        ),
        "lang_set": "✅ Til o'rnatildi: O'zbekcha 🇺🇿",
        "main_menu": "📋 <b>Asosiy menyu</b>\n\nQuyidagi tugmalardan birini tanlang:",
        "btn_apply": "📝 Ariza berish",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "btn_faq": "❓ Ko'p so'raladigan savollar",
        "btn_cancel": "❌ Bekor qilish",
        "btn_back": "⬅️ Ortga",
        "btn_skip": "⏭ O'tkazib yuborish",
        "cancelled": "❌ Ariza bekor qilindi. Asosiy menyuga qaytdingiz.",
        "already_applied": (
            "⚠️ <b>Siz allaqachon ariza topshirgansiz.</b>\n\n"
            "Har bir nomzoddan faqat bitta ariza qabul qilinadi.\n"
            "Ma'lumotlarni o'zgartirish kerak bo'lsa, yotoqxona ma'muriyatiga murojaat qiling."
        ),
        "already_applied_with_id": (
            "⚠️ <b>Siz allaqachon ariza topshirgansiz.</b>\n\n"
            "🆔 Ariza raqami: <b>{id}</b>\n\n"
            "Har bir nomzoddan faqat bitta ariza qabul qilinadi.\n"
            "Ma'lumotlarni o'zgartirish kerak bo'lsa, yotoqxona ma'muriyatiga murojaat qiling."
        ),
        "submit_error": "❌ Arizani yuborishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
        # Oferta
        "oferta_message": (
            "📜 <b>Oferta shartnomasi</b>\n\n"
            "Davom etishdan oldin, iltimos oferta shartnomasini diqqat bilan o'qing.\n\n"
            "Oferta shartlarini qabul qilasizmi?"
        ),
        "oferta_link": "Ofertani ko'rish",
        "btn_oferta_agree": "✅ Qabul qilaman",
        # Sex
        "ask_sex": "👤 <b>Jinsingizni tanlang:</b>",
        "btn_male": "👨 Erkak",
        "btn_female": "👩 Ayol",
        "sex_male": "Erkak",
        "sex_female": "Ayol",
        "preview_sex": "👤 <b>Jins:</b> {value}",
        # Region
        "region_foreign": "🌍 Xorijiy davlat",
        # Application form prompts
        "ask_full_name": "👤 <b>To'liq ismingizni kiriting</b> (F.I.O.):\n\n<i>Misol: Karimov Jasur Bahodirovich</i>",
        "ask_level": "🎓 <b>Kursni tanlang:</b>",
        "ask_faculty": "🏛 <b>Ta'lim yo'nalishini tanlang:</b>",
        "ask_region": "📍 <b>Hududni tanlang:</b>",
        "ask_town": "🏘 <b>Tuman/shaharni tanlang:</b>\n\n<i>Viloyat: {region}</i>",
        "ask_town_custom": "✏️ <b>Tuman/shahar nomini kiriting:</b>",
        "ask_reason": "📝 <b>Yotoqxonaga joylashish sababini tanlang:</b>",
        "ask_reason_custom": "✏️ <b>Sababni yozing:</b>",
        "ask_official_doc": (
            "📄 <b>Rasmiy hujjatni yuboring:</b>\n\n"
            "<i>Tegishli rasmiy hujjatni yuboring — rasm yoki fayl\n"
            "(PDF, Word, taqdimot va h.k.)</i>"
        ),
        "ask_official_doc_invalid": "⚠️ Iltimos, rasm yoki hujjat fayli (PDF, Word, taqdimot) yuboring.",
        "ask_passport": "📸 <b>Pasport rasmini yuboring:</b>\n\n<i>Pasportning asosiy sahifasi rasmini yuboring</i>",
        "ask_photo_3x4": "🖼 <b>3x4 rasmingizni yuboring:</b>\n\n<i>Standart 3x4 formatdagi rasmingizni yuboring</i>",
        "ask_phone": (
            "📞 <b>Telefon raqamingizni yuboring:</b>\n\n"
            "<i>Tugmani bosing yoki +998XXXXXXXXX formatida kiriting.\n"
            "Chet el raqami bo'lsa, mamlakat kodi bilan kiriting, masalan +905XXXXXXXX</i>"
        ),
        "ask_additional_phone": (
            "📞 <b>Qo'shimcha telefon raqamni kiriting:</b>\n\n"
            "<i>+998XXXXXXXXX formatida kiriting.\n"
            "Chet el raqami bo'lsa, mamlakat kodi bilan kiriting, masalan +905XXXXXXXX</i>"
        ),
        "btn_share_phone": "📱 Telefon raqamni yuborish",
        # Validation
        "invalid_name": "⚠️ Ism kamida 5 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:",
        "send_photo_only": "⚠️ Iltimos, rasm yoki fayl yuboring.",
        "invalid_phone": (
            "⚠️ Telefon raqami noto'g'ri. +998XXXXXXXXX formatida kiriting yoki tugmani bosing.\n"
            "Chet el raqamini mamlakat kodi bilan, «+» belgisidan boshlab kiriting."
        ),
        "same_phone_error": "⚠️ Qo'shimcha raqam asosiy telefon raqamidan farq qilishi kerak.",
        # Preview
        "preview_title": "📋 <b>Arizangizni tekshiring:</b>\n",
        "preview_name": "👤 <b>F.I.O.:</b> {value}",
        "preview_level": "🎓 <b>Kurs:</b> {value}-kurs",
        "preview_faculty": "🏛 <b>Yo'nalish:</b> {value}",
        "preview_region": "📍 <b>Viloyat:</b> {value}",
        "preview_town": "🏘 <b>Tuman/Shahar:</b> {value}",
        "preview_reason": "📝 <b>Sabab:</b> {value}",
        "preview_official_doc": "📄 <b>Rasmiy hujjat:</b> ✅ Yuklangan",
        "preview_phone": "📞 <b>Telefon:</b> {value}",
        "preview_additional_phone": "📞 <b>Qo'shimcha telefon:</b> {value}",
        "preview_photos": "📸 <b>Rasmlar:</b> ✅ Yuklangan",
        "preview_footer": "\n<i>Ma'lumotlarni tekshiring va tasdiqlang</i>",
        "btn_confirm": "✅ Tasdiqlash",
        "btn_edit": "✏️ Tahrirlash",
        # Edit
        "edit_select": "✏️ <b>Qaysi maydonni o'zgartirmoqchisiz?</b>",
        "edit_name": "👤 F.I.O.",
        "edit_sex": "👤 Jins",
        "edit_level": "🎓 Kurs",
        "edit_faculty": "🏛 Yo'nalish",
        "edit_region": "📍 Viloyat",
        "edit_town": "🏘 Tuman/Shahar",
        "edit_reason": "📝 Sabab",
        "edit_official_doc": "📄 Rasmiy hujjat",
        "edit_passport": "📸 Pasport rasmi",
        "edit_photo": "🖼 3x4 rasm",
        "edit_phone": "📞 Telefon",
        "edit_additional_phone": "📞 Qo'shimcha tel.",
        # Confirmation
        "confirmed": (
            "🎉🎊 <b>Arizangiz muvaffaqiyatli yuborildi!</b> 🎊🎉\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Ariza raqami: <b>#{id}</b>\n"
            "✅ Hujjatlaringiz qabul qilindi.\n"
            "🕓 Arizangiz ishchi guruh tomonidan 10-avgustga qadar ko‘rib chiqiladi.\n"
            "🔔 Natija ushbu bot orqali e'lon qilinadi!\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤝 E'tiboringiz uchun rahmat! Omad tilaymiz! 🍀"
        ),
        # Admin / results
        "btn_publish_results": "📣 Tayyor natijalarni yuborish",
        "publish_prompt": (
            "📣 <b>Natijalarni yuborish</b>\n\n"
            "Bot jadvalni doimiy kuzatadi va har bir arizachiga natijani o‘zi yuboradi. "
            "Bu tugma shu tekshiruvni hoziroq bajaradi.\n\n"
            "Qator yuborilishi uchun:\n"
            "• <b>M</b> — holat: <b>2</b> qabul qilindi, <b>1</b> suhbatga, <b>0</b> rad etildi\n"
            "• <b>N</b> — izoh, arizachiga ko‘rinadi. <b>2</b> va <b>0</b> uchun majburiy; "
            "<b>1</b> uchun bo‘sh qoldirilsa, xabarda izoh ko‘rsatilmaydi\n"
            "• matn <b>{minutes} daqiqa</b> o‘zgarmagan bo‘lishi kerak\n\n"
            "📅 <b>1</b> qo‘yilgan qator izohsiz yuboriladi. Suhbat sanasi ma'lum bo‘lgach, "
            "<b>N</b> ga sana va kerakli ma'lumotlarni yozing — bot uni alohida xabar "
            "sifatida yuboradi (har bir qatorga bir marta).\n\n"
            "Davom etasizmi?"
        ),
        "btn_publish_confirm": "✅ Ha, yuborilsin",
        "btn_publish_cancel": "❌ Bekor qilish",
        "publish_cancelled": "❌ Natijalarni yuborish bekor qilindi.",
        "publishing": "⏳ Natijalar yuborilmoqda, iltimos kuting...",
        "publish_done": (
            "✅ <b>Tekshiruv yakunlandi</b>\n\n"
            "🎉 Qabul qilindi (2): <b>{accepted}</b>\n"
            "🗣 Suhbatga taklif (1): <b>{interview}</b>\n"
            "❌ Rad etildi (0): <b>{rejected}</b>\n"
            "📅 Suhbat ma'lumoti yuborildi: <b>{details}</b>\n"
            "🔄 Yangilangan natija yuborildi: <b>{updated}</b>\n"
            "⚠️ Yuborilmadi: <b>{failed}</b>\n\n"
            "⏳ Matn hali o‘zgarib turibdi: <b>{waiting}</b>\n"
            "📝 Suhbat izohi kutilmoqda (N bo‘sh): <b>{no_details}</b>\n"
            "✍️ Holat yoki izoh to‘ldirilmagan: <b>{pending}</b>\n"
            "⬜️ Hali ko‘rib chiqilmagan: <b>{undecided}</b>"
        ),
        "not_admin": "⛔️ Bu amal faqat administratorlar uchun.",
        "reapply_usage": "ℹ️ Foydalanish: <code>/allow_reapply &lt;telegram_id&gt;</code>",
        "reapply_done": (
            "✅ <b>{id}</b> foydalanuvchisi yangi ariza topshirishi mumkin.\n\n"
            "<i>Eski ariza kanalda va jadvalda qoladi — kerak bo'lsa qo'lda o'chiring.</i>"
        ),
        "reapply_not_found": "ℹ️ <b>{id}</b> foydalanuvchisidan ariza topilmadi.",
        "resend_usage": "ℹ️ Foydalanish: <code>/resend &lt;ariza raqami&gt;</code>",
        "resend_done": (
            "✅ <b>#{id}</b> arizasi bo‘yicha natija qayta yuboriladi.\n\n"
            "<i>Jadvaldagi holat va izoh bir necha daqiqa o‘zgarmasa, bot uni o‘zi yuboradi.</i>"
        ),
        "resend_not_found": "ℹ️ <b>#{id}</b> arizasi bo‘yicha yuborilgan natija topilmadi.",
        "result_accepted": (
            "🎉🎊 <b>Tabriklaymiz!</b> 🎊🎉\n\n"
            "✅ Siz TTPU yotoqxonasiga <b>qabul qilindingiz!</b>\n\n"
            "💬 <b>Ishchi guruh izohi:</b>\n{reason}\n\n"
            "📞 Keyingi qadamlar bo‘yicha siz bilan bog‘lanamiz.\n"
            "🍀 Omad yor bo‘lsin!"
        ),
        "result_interview": (
            "📩 <b>Natija</b>\n\n"
            "🗣 Arizangiz ko‘rib chiqildi — siz <b>suhbatga taklif qilinasiz!</b>\n\n"
            "💬 <b>Ishchi guruh izohi:</b>\n{reason}\n\n"
            "🍀 Omad!"
        ),
        # Same decision, but the tutors have not written anything yet — no empty
        # "comment" section, and a promise of the details to come.
        "result_interview_no_reason": (
            "📩 <b>Natija</b>\n\n"
            "🗣 Arizangiz ko‘rib chiqildi — siz <b>suhbatga taklif qilinasiz!</b>\n\n"
            "📅 Suhbat sanasi belgilangach, barcha ma'lumotlarni shu yerda yuboramiz.\n"
            "🔔 Xabarlarni o‘tkazib yubormaslik uchun botni bloklamang.\n\n"
            "🍀 Omad!"
        ),
        # The follow-up: the date and everything else the tutors typed into N.
        "result_interview_details": (
            "📅 <b>Suhbat haqida ma'lumot</b>\n\n"
            "{reason}\n\n"
            "🍀 Omad tilaymiz!"
        ),
        "result_rejected": (
            "📩 <b>Natija</b>\n\n"
            "❌ Afsuski, arizangiz <b>rad etildi.</b>\n\n"
            "💬 <b>Sabab:</b>\n{reason}\n"
        ),
        # Appended to a reason that was machine-translated, so the applicant can
        # always read what the tutors actually wrote.
        "reason_original": (
            "\n\n🖊 <i>Ishchi guruh yozgan asl matn:</i>\n<i>{original}</i>"
        ),
        # Put in front of any result that is being sent a second time, because the
        # tutors changed the decision or the reason. Without it the applicant is
        # left holding two different answers with no way to tell which is current.
        "result_updated": (
            "🔄 <b>Natijangiz yangilandi.</b>\n"
            "<i>Quyidagi xabar avvalgisining o‘rniga keladi.</i>\n\n"
        ),
        # Channel (always sent in Uzbek)
        "channel_caption": (
            "📋 <b>YANGI ARIZA #{id}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>F.I.O.:</b> {name}\n"
            "👤 <b>Jins:</b> {sex}\n"
            "🎓 <b>Kurs:</b> {level}-kurs\n"
            "🏛 <b>Yo'nalish:</b> {faculty}\n"
            "📍 <b>Viloyat:</b> {region}\n"
            "🏘 <b>Tuman:</b> {town}\n"
            "📝 <b>Sabab:</b> {reason}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "📞 <b>Qo'shimcha:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        # Preview (same layout, user's language)
        "preview_caption": (
            "📋 <b>ARIZA KO'RINISHI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>F.I.O.:</b> {name}\n"
            "👤 <b>Jins:</b> {sex}\n"
            "🎓 <b>Kurs:</b> {level}-kurs\n"
            "🏛 <b>Yo'nalish:</b> {faculty}\n"
            "📍 <b>Viloyat:</b> {region}\n"
            "🏘 <b>Tuman:</b> {town}\n"
            "📝 <b>Sabab:</b> {reason}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "📞 <b>Qo'shimcha:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        # FAQ
        "faq_title": "❓ <b>Ko'p so'raladigan savollar</b>\n",
        "faq_content": (
            "<b>1. Ariza qanday beriladi?</b>\n"
            "📝 Ariza berish tugmasini bosing va barcha ma'lumotlarni kiriting.\n\n"
            "<b>2. Qanday hujjatlar kerak?</b>\n"
            "📸 Pasportning asosiy sahifasi rasmi va 3x4 formatdagi rasm.\n\n"
            "<b>3. Natijalar qachon e'lon qilinadi?</b>\n"
            "📅 Natijalar arizalar to'planganidan so'ng e'lon qilinadi.\n\n"
            "<b>4. Aloqa:</b>\n"
            "📞 Qo'shimcha savollar uchun universitetga murojaat qiling."
        ),
        "other": "📌 Boshqa",
        "level_year": "{n}-kurs",
    },
    "en": {
        "welcome": (
            "🏛 <b>TTPU Dormitory Application Bot</b>\n\n"
            "Hello! Please select your language:"
        ),
        "lang_set": "✅ Language set: English 🇬🇧",
        "main_menu": "📋 <b>Main Menu</b>\n\nSelect one of the options below:",
        "btn_apply": "📝 Apply",
        "btn_change_lang": "🌐 Change Language",
        "btn_faq": "❓ FAQ",
        "btn_cancel": "❌ Cancel",
        "btn_back": "⬅️ Back",
        "btn_skip": "⏭ Skip",
        "cancelled": "❌ Application cancelled. You are back in the main menu.",
        "already_applied": (
            "⚠️ <b>You have already submitted an application.</b>\n\n"
            "Only one application per applicant is accepted.\n"
            "If you need to change something, contact the dormitory administration."
        ),
        "already_applied_with_id": (
            "⚠️ <b>You have already submitted an application.</b>\n\n"
            "🆔 Application number: <b>{id}</b>\n\n"
            "Only one application per applicant is accepted.\n"
            "If you need to change something, contact the dormitory administration."
        ),
        "submit_error": "❌ Something went wrong while submitting your application. Please try again.",
        # Oferta
        "oferta_message": (
            "📜 <b>User Agreement</b>\n\n"
            "Before continuing, please read our offer agreement carefully.\n\n"
            "Do you accept the terms of the agreement?"
        ),
        "oferta_link": "View Agreement",
        "btn_oferta_agree": "✅ I agree",
        # Sex
        "ask_sex": "👤 <b>Select your gender:</b>",
        "btn_male": "👨 Male",
        "btn_female": "👩 Female",
        "sex_male": "Male",
        "sex_female": "Female",
        "preview_sex": "👤 <b>Gender:</b> {value}",
        # Region
        "region_foreign": "🌍 Foreign",
        # Application form
        "ask_full_name": "👤 <b>Enter your full name:</b>\n\n<i>Example: Karimov Jasur Bakhodirovich</i>",
        "ask_level": "🎓 <b>Select your year:</b>",
        "ask_faculty": "🏛 <b>Select your direction:</b>",
        "ask_region": "📍 <b>Select your location:</b>",
        "ask_town": "🏘 <b>Select your town/district:</b>\n\n<i>Region: {region}</i>",
        "ask_town_custom": "✏️ <b>Type your town/district name:</b>",
        "ask_reason": "📝 <b>Select the reason for accommodation in the dormitory:</b>",
        "ask_reason_custom": "✏️ <b>Type your reason:</b>",
        "ask_official_doc": (
            "📄 <b>Send your official document:</b>\n\n"
            "<i>Send the relevant official document — photo or file\n"
            "(PDF, Word, presentation, etc.)</i>"
        ),
        "ask_official_doc_invalid": "⚠️ Please send a photo or document file (PDF, Word, presentation).",
        "ask_passport": "📸 <b>Send your passport photo:</b>\n\n<i>Send a photo of the main page of your passport</i>",
        "ask_photo_3x4": "🖼 <b>Send your 3x4 photo:</b>\n\n<i>Send a standard 3x4 format photo</i>",
        "ask_phone": (
            "📞 <b>Send your phone number:</b>\n\n"
            "<i>Press the button or type in +998XXXXXXXXX format.\n"
            "For a foreign number, include the country code, e.g. +905XXXXXXXX</i>"
        ),
        "ask_additional_phone": (
            "📞 <b>Enter additional phone number:</b>\n\n"
            "<i>Enter in +998XXXXXXXXX format.\n"
            "For a foreign number, include the country code, e.g. +905XXXXXXXX</i>"
        ),
        "btn_share_phone": "📱 Share Phone Number",
        "invalid_name": "⚠️ Name must be at least 5 characters. Please try again:",
        "send_photo_only": "⚠️ Please send a photo or image file.",
        "invalid_phone": (
            "⚠️ Invalid phone number. Please use +998XXXXXXXXX format or press the button.\n"
            "Foreign numbers must start with «+» and include the country code."
        ),
        "same_phone_error": "⚠️ Additional number must be different from the main phone number.",
        "preview_title": "📋 <b>Review your application:</b>\n",
        "preview_name": "👤 <b>Full Name:</b> {value}",
        "preview_sex": "👤 <b>Gender:</b> {value}",
        "preview_level": "🎓 <b>Year:</b> {value}",
        "preview_faculty": "🏛 <b>Direction:</b> {value}",
        "preview_region": "📍 <b>Region:</b> {value}",
        "preview_town": "🏘 <b>Town/District:</b> {value}",
        "preview_reason": "📝 <b>Reason:</b> {value}",
        "preview_official_doc": "📄 <b>Official document:</b> ✅ Uploaded",
        "preview_phone": "📞 <b>Phone:</b> {value}",
        "preview_additional_phone": "📞 <b>Additional phone:</b> {value}",
        "preview_photos": "📸 <b>Photos:</b> ✅ Uploaded",
        "preview_footer": "\n<i>Please review and confirm your information</i>",
        "btn_confirm": "✅ Confirm",
        "btn_edit": "✏️ Edit",
        "edit_select": "✏️ <b>Which field would you like to edit?</b>",
        "edit_name": "👤 Full Name",
        "edit_sex": "👤 Gender",
        "edit_level": "🎓 Year",
        "edit_faculty": "🏛 Direction",
        "edit_region": "📍 Region",
        "edit_town": "🏘 Town/District",
        "edit_reason": "📝 Reason",
        "edit_official_doc": "📄 Official doc",
        "edit_passport": "📸 Passport Photo",
        "edit_photo": "🖼 3x4 Photo",
        "edit_phone": "📞 Phone",
        "edit_additional_phone": "📞 Add. phone",
        "confirmed": (
            "🎉🎊 <b>Your application has been submitted successfully!</b> 🎊🎉\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Application number: <b>#{id}</b>\n"
            "✅ Your documents have been received.\n"
            "🕓 Your application will be reviewed by the working group by August 10.\n"
            "🔔 The result will be announced through this bot!\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤝 Thank you! Good luck! 🍀"
        ),
        # Admin / results
        "btn_publish_results": "📣 Send finished results",
        "publish_prompt": (
            "📣 <b>Send results</b>\n\n"
            "The bot watches the sheet and sends each applicant their result on its own. "
            "This button just runs that check right now.\n\n"
            "A row is sent when:\n"
            "• <b>M</b> — status: <b>2</b> accepted, <b>1</b> invited to an interview, <b>0</b> rejected\n"
            "• <b>N</b> — reason, the applicant sees it. Required for <b>2</b> and <b>0</b>; "
            "leave it empty for <b>1</b> and no comment is shown in the message\n"
            "• the text has not changed for <b>{minutes} minutes</b>\n\n"
            "📅 A row marked <b>1</b> goes out without a comment. Once the interview date "
            "is known, write it — and anything else the applicant needs — into <b>N</b>, "
            "and the bot sends it as a separate message (once per row).\n\n"
            "Do you want to continue?"
        ),
        "btn_publish_confirm": "✅ Yes, send",
        "btn_publish_cancel": "❌ Cancel",
        "publish_cancelled": "❌ Sending results was cancelled.",
        "publishing": "⏳ Sending results, please wait...",
        "publish_done": (
            "✅ <b>Check finished</b>\n\n"
            "🎉 Accepted (2): <b>{accepted}</b>\n"
            "🗣 Invited to an interview (1): <b>{interview}</b>\n"
            "❌ Rejected (0): <b>{rejected}</b>\n"
            "📅 Interview details sent: <b>{details}</b>\n"
            "🔄 Updated results sent: <b>{updated}</b>\n"
            "⚠️ Failed to deliver: <b>{failed}</b>\n\n"
            "⏳ Text still being edited: <b>{waiting}</b>\n"
            "📝 Waiting for interview details (N empty): <b>{no_details}</b>\n"
            "✍️ Status or reason missing: <b>{pending}</b>\n"
            "⬜️ Not reviewed yet: <b>{undecided}</b>"
        ),
        "not_admin": "⛔️ This action is for administrators only.",
        "reapply_usage": "ℹ️ Usage: <code>/allow_reapply &lt;telegram_id&gt;</code>",
        "reapply_done": (
            "✅ User <b>{id}</b> can submit a new application.\n\n"
            "<i>The old application stays in the channel and the sheet — remove it by hand if needed.</i>"
        ),
        "reapply_not_found": "ℹ️ No application on record for user <b>{id}</b>.",
        "resend_usage": "ℹ️ Usage: <code>/resend &lt;application id&gt;</code>",
        "resend_done": (
            "✅ The result for application <b>#{id}</b> will be sent again.\n\n"
            "<i>It goes out once the status and reason in the sheet have been unchanged for a few minutes.</i>"
        ),
        "resend_not_found": "ℹ️ No result has been sent for application <b>#{id}</b>.",
        "result_accepted": (
            "🎉🎊 <b>Congratulations!</b> 🎊🎉\n\n"
            "✅ You have been <b>accepted</b> to the TTPU dormitory!\n\n"
            "💬 <b>Comment from the working group:</b>\n{reason}\n\n"
            "📞 We will contact you about the next steps.\n"
            "🍀 Best of luck!"
        ),
        "result_interview": (
            "📩 <b>Result</b>\n\n"
            "🗣 Your application has been reviewed — you are <b>invited to an interview!</b>\n\n"
            "💬 <b>Comment from the working group:</b>\n{reason}\n\n"
            "📞 We will contact you about the time and place.\n"
            "🍀 Good luck!"
        ),
        "result_interview_no_reason": (
            "📩 <b>Result</b>\n\n"
            "🗣 Your application has been reviewed — you are <b>invited to an interview!</b>\n\n"
            "📅 As soon as the interview date is set, we will send you all the details here.\n"
            "🔔 Please do not block the bot, so you do not miss the message.\n\n"
            "🍀 Good luck!"
        ),
        "result_interview_details": (
            "📅 <b>Interview details</b>\n\n"
            "{reason}\n\n"
            "🍀 Good luck!"
        ),
        "result_rejected": (
            "📩 <b>Result</b>\n\n"
            "Unfortunately, you were <b>not accepted</b> to the dormitory this time.\n\n"
            "💬 <b>Reason:</b>\n{reason}\n\n"
            "🙏 Thank you for your application. We will get in touch if a place opens up."
        ),
        "reason_original": (
            "\n\n🖊 <i>Original wording from the committee:</i>\n<i>{original}</i>"
        ),
        "result_updated": (
            "🔄 <b>Your result has been updated.</b>\n"
            "<i>The message below replaces the one you received earlier.</i>\n\n"
        ),
        "channel_caption": (
            "📋 <b>NEW APPLICATION #{id}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>Full Name:</b> {name}\n"
            "👤 <b>Gender:</b> {sex}\n"
            "🎓 <b>Year:</b> {level}\n"
            "🏛 <b>Direction:</b> {faculty}\n"
            "📍 <b>Region:</b> {region}\n"
            "🏘 <b>Town:</b> {town}\n"
            "📝 <b>Reason:</b> {reason}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📞 <b>Additional:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "preview_caption": (
            "📋 <b>APPLICATION PREVIEW</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>Full Name:</b> {name}\n"
            "👤 <b>Gender:</b> {sex}\n"
            "🎓 <b>Year:</b> {level}\n"
            "🏛 <b>Direction:</b> {faculty}\n"
            "📍 <b>Region:</b> {region}\n"
            "🏘 <b>Town:</b> {town}\n"
            "📝 <b>Reason:</b> {reason}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📞 <b>Additional:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "faq_title": "❓ <b>Frequently Asked Questions</b>\n",
        "faq_content": (
            "<b>1. How do I apply?</b>\n"
            "📝 Press the Apply button and fill in all the required information.\n\n"
            "<b>2. What documents are needed?</b>\n"
            "📸 A photo of the main page of your passport and a 3x4 format photo.\n\n"
            "<b>3. When are results announced?</b>\n"
            "📅 Results will be announced after all applications are collected.\n\n"
            "<b>4. Contact:</b>\n"
            "📞 For additional questions, please contact the university."
        ),
        "other": "📌 Other",
        "level_year": "Year {n}",
    },
    "ru": {
        "welcome": (
            "🏛 <b>Бот заявки в общежитие ТТПУ</b>\n\n"
            "Здравствуйте! Пожалуйста, выберите язык:"
        ),
        "lang_set": "✅ Язык установлен: Русский 🇷🇺",
        "main_menu": "📋 <b>Главное меню</b>\n\nВыберите один из вариантов ниже:",
        "btn_apply": "📝 Подать заявку",
        "btn_change_lang": "🌐 Изменить язык",
        "btn_faq": "❓ Часто задаваемые вопросы",
        "btn_cancel": "❌ Отменить",
        "btn_back": "⬅️ Назад",
        "btn_skip": "⏭ Пропустить",
        "cancelled": "❌ Заявка отменена. Вы вернулись в главное меню.",
        "already_applied": (
            "⚠️ <b>Вы уже подали заявку.</b>\n\n"
            "От одного абитуриента принимается только одна заявка.\n"
            "Если нужно что-то изменить, обратитесь к администрации общежития."
        ),
        "already_applied_with_id": (
            "⚠️ <b>Вы уже подали заявку.</b>\n\n"
            "🆔 Номер заявки: <b>{id}</b>\n\n"
            "От одного абитуриента принимается только одна заявка.\n"
            "Если нужно что-то изменить, обратитесь к администрации общежития."
        ),
        "submit_error": "❌ Произошла ошибка при отправке заявки. Пожалуйста, попробуйте снова.",
        # Oferta
        "oferta_message": (
            "📜 <b>Договор оферты</b>\n\n"
            "Перед продолжением, пожалуйста, внимательно прочитайте договор оферты.\n\n"
            "Вы принимаете условия договора?"
        ),
        "oferta_link": "Просмотреть оферту",
        "btn_oferta_agree": "✅ Согласен",
        # Sex
        "ask_sex": "👤 <b>Выберите ваш пол:</b>",
        "btn_male": "👨 Мужской",
        "btn_female": "👩 Женский",
        "sex_male": "Мужской",
        "sex_female": "Женский",
        "preview_sex": "👤 <b>Пол:</b> {value}",
        # Region
        "region_foreign": "🌍 Иностранец",
        # Application form
        "ask_full_name": "👤 <b>Введите ваше полное имя</b> (Ф.И.О.):\n\n<i>Пример: Каримов Жасур Баходирович</i>",
        "ask_level": "🎓 <b>Выберите курс:</b>",
        "ask_faculty": "🏛 <b>Выберите направление:</b>",
        "ask_region": "📍 <b>Выберите расположение:</b>",
        "ask_town": "🏘 <b>Выберите район/город:</b>\n\n<i>Область: {region}</i>",
        "ask_town_custom": "✏️ <b>Введите название района/города:</b>",
        "ask_reason": "📝 <b>Выберите причину проживания в общежитии.:</b>",
        "ask_reason_custom": "✏️ <b>Напишите причину:</b>",
        "ask_official_doc": (
            "📄 <b>Отправьте официальный документ:</b>\n\n"
            "<i>Отправьте соответствующий официальный документ — фото или файл\n"
            "(PDF, Word, презентация и т.д.)</i>"
        ),
        "ask_official_doc_invalid": "⚠️ Пожалуйста, отправьте фото или файл документа (PDF, Word, презентация).",
        "ask_passport": "📸 <b>Отправьте фото паспорта:</b>\n\n<i>Отправьте фото основной страницы паспорта</i>",
        "ask_photo_3x4": "🖼 <b>Отправьте фото 3x4:</b>\n\n<i>Отправьте фото стандартного формата 3x4</i>",
        "ask_phone": (
            "📞 <b>Отправьте номер телефона:</b>\n\n"
            "<i>Нажмите кнопку или введите в формате +998XXXXXXXXX.\n"
            "Для зарубежного номера укажите код страны, например +905XXXXXXXX</i>"
        ),
        "ask_additional_phone": (
            "📞 <b>Введите дополнительный номер телефона:</b>\n\n"
            "<i>Введите в формате +998XXXXXXXXX.\n"
            "Для зарубежного номера укажите код страны, например +905XXXXXXXX</i>"
        ),
        "btn_share_phone": "📱 Отправить номер телефона",
        "invalid_name": "⚠️ Имя должно содержать минимум 5 символов. Попробуйте снова:",
        "send_photo_only": "⚠️ Пожалуйста, отправьте фото или файл изображения.",
        "invalid_phone": (
            "⚠️ Неверный номер телефона. Используйте формат +998XXXXXXXXX или нажмите кнопку.\n"
            "Зарубежный номер вводите с «+» и кодом страны."
        ),
        "same_phone_error": "⚠️ Дополнительный номер должен отличаться от основного.",
        "preview_title": "📋 <b>Проверьте вашу заявку:</b>\n",
        "preview_name": "👤 <b>Ф.И.О.:</b> {value}",
        "preview_sex": "👤 <b>Пол:</b> {value}",
        "preview_level": "🎓 <b>Курс:</b> {value}-курс",
        "preview_faculty": "🏛 <b>Направление:</b> {value}",
        "preview_region": "📍 <b>Область:</b> {value}",
        "preview_town": "🏘 <b>Район/Город:</b> {value}",
        "preview_reason": "📝 <b>Причина:</b> {value}",
        "preview_official_doc": "📄 <b>Официальный документ:</b> ✅ Загружен",
        "preview_phone": "📞 <b>Телефон:</b> {value}",
        "preview_additional_phone": "📞 <b>Доп. телефон:</b> {value}",
        "preview_photos": "📸 <b>Фотографии:</b> ✅ Загружены",
        "preview_footer": "\n<i>Проверьте данные и подтвердите</i>",
        "btn_confirm": "✅ Подтвердить",
        "btn_edit": "✏️ Редактировать",
        "edit_select": "✏️ <b>Какое поле вы хотите изменить?</b>",
        "edit_name": "👤 Ф.И.О.",
        "edit_sex": "👤 Пол",
        "edit_level": "🎓 Курс",
        "edit_faculty": "🏛 Направление",
        "edit_region": "📍 Область",
        "edit_town": "🏘 Район/Город",
        "edit_reason": "📝 Причина",
        "edit_official_doc": "📄 Офиц. документ",
        "edit_passport": "📸 Фото паспорта",
        "edit_photo": "🖼 Фото 3x4",
        "edit_phone": "📞 Телефон",
        "edit_additional_phone": "📞 Доп. телефон",
        "confirmed": (
            "🎉🎊 <b>Ваша заявка успешно отправлена!</b> 🎊🎉\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Номер заявки: <b>#{id}</b>\n"
            "✅ Ваши документы приняты.\n"
            "🕓 Заявка будет рассмотрена рабочей группой до 10 августа.\n"
            "🔔 Результат будет объявлен через этого бота!\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤝 Спасибо! Удачи! 🍀"
        ),
        # Admin / results
        "btn_publish_results": "📣 Отправить готовые результаты",
        "publish_prompt": (
            "📣 <b>Отправка результатов</b>\n\n"
            "Бот сам следит за таблицей и отправляет каждому заявителю его результат. "
            "Эта кнопка просто выполняет проверку прямо сейчас.\n\n"
            "Строка отправляется, если:\n"
            "• <b>M</b> — статус: <b>2</b> принят, <b>1</b> приглашён на собеседование, <b>0</b> отклонён\n"
            "• <b>N</b> — комментарий, его увидит заявитель. Обязателен для <b>2</b> и <b>0</b>; "
            "для <b>1</b> можно оставить пустым — тогда в сообщении комментария не будет\n"
            "• текст не менялся <b>{minutes} минут</b>\n\n"
            "📅 Строка со статусом <b>1</b> уходит без комментария. Когда дата собеседования "
            "станет известна, впишите её и всё остальное в <b>N</b> — бот отправит это "
            "отдельным сообщением (один раз на строку).\n\n"
            "Продолжить?"
        ),
        "btn_publish_confirm": "✅ Да, отправить",
        "btn_publish_cancel": "❌ Отмена",
        "publish_cancelled": "❌ Отправка результатов отменена.",
        "publishing": "⏳ Отправка результатов, пожалуйста, подождите...",
        "publish_done": (
            "✅ <b>Проверка завершена</b>\n\n"
            "🎉 Приняты (2): <b>{accepted}</b>\n"
            "🗣 На собеседование (1): <b>{interview}</b>\n"
            "❌ Отклонены (0): <b>{rejected}</b>\n"
            "📅 Отправлена информация о собеседовании: <b>{details}</b>\n"
            "🔄 Отправлено обновлённых результатов: <b>{updated}</b>\n"
            "⚠️ Не доставлено: <b>{failed}</b>\n\n"
            "⏳ Текст ещё редактируется: <b>{waiting}</b>\n"
            "📝 Ждём информацию о собеседовании (N пуст): <b>{no_details}</b>\n"
            "✍️ Нет статуса или комментария: <b>{pending}</b>\n"
            "⬜️ Ещё не рассмотрены: <b>{undecided}</b>"
        ),
        "not_admin": "⛔️ Это действие доступно только администраторам.",
        "reapply_usage": "ℹ️ Использование: <code>/allow_reapply &lt;telegram_id&gt;</code>",
        "reapply_done": (
            "✅ Пользователь <b>{id}</b> может подать новую заявку.\n\n"
            "<i>Старая заявка останется в канале и таблице — удалите её вручную при необходимости.</i>"
        ),
        "reapply_not_found": "ℹ️ Заявка пользователя <b>{id}</b> не найдена.",
        "resend_usage": "ℹ️ Использование: <code>/resend &lt;номер заявки&gt;</code>",
        "resend_done": (
            "✅ Результат по заявке <b>#{id}</b> будет отправлен повторно.\n\n"
            "<i>Он уйдёт, когда статус и комментарий в таблице не будут меняться несколько минут.</i>"
        ),
        "resend_not_found": "ℹ️ По заявке <b>#{id}</b> результат не отправлялся.",
        "result_accepted": (
            "🎉🎊 <b>Поздравляем!</b> 🎊🎉\n\n"
            "✅ Вы <b>приняты</b> в общежитие TTPU!\n\n"
            "💬 <b>Комментарий рабочей группы:</b>\n{reason}\n\n"
            "📞 Мы свяжемся с вами по поводу дальнейших шагов.\n"
            "🍀 Удачи!"
        ),
        "result_interview": (
            "📩 <b>Результат</b>\n\n"
            "🗣 Ваша заявка рассмотрена — вы <b>приглашены на собеседование!</b>\n\n"
            "💬 <b>Комментарий рабочей группы:</b>\n{reason}\n\n"
            "📞 Мы свяжемся с вами по поводу времени и места.\n"
            "🍀 Удачи!"
        ),
        "result_interview_no_reason": (
            "📩 <b>Результат</b>\n\n"
            "🗣 Ваша заявка рассмотрена — вы <b>приглашены на собеседование!</b>\n\n"
            "📅 Как только дата собеседования будет назначена, мы пришлём сюда все подробности.\n"
            "🔔 Пожалуйста, не блокируйте бота, чтобы не пропустить сообщение.\n\n"
            "🍀 Удачи!"
        ),
        "result_interview_details": (
            "📅 <b>Информация о собеседовании</b>\n\n"
            "{reason}\n\n"
            "🍀 Удачи!"
        ),
        "result_rejected": (
            "📩 <b>Результат</b>\n\n"
            "К сожалению, в этот раз вы <b>не приняты</b> в общежитие.\n\n"
            "💬 <b>Причина:</b>\n{reason}\n\n"
            "🙏 Спасибо за вашу заявку. Мы свяжемся с вами, если появится место."
        ),
        "reason_original": (
            "\n\n🖊 <i>Оригинал, как написала комиссия:</i>\n<i>{original}</i>"
        ),
        "result_updated": (
            "🔄 <b>Ваш результат обновлён.</b>\n"
            "<i>Сообщение ниже заменяет предыдущее.</i>\n\n"
        ),
        "channel_caption": (
            "📋 <b>НОВАЯ ЗАЯВКА #{id}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>Ф.И.О.:</b> {name}\n"
            "👤 <b>Пол:</b> {sex}\n"
            "🎓 <b>Курс:</b> {level}-курс\n"
            "🏛 <b>Направление:</b> {faculty}\n"
            "📍 <b>Область:</b> {region}\n"
            "🏘 <b>Район:</b> {town}\n"
            "📝 <b>Причина:</b> {reason}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📞 <b>Доп. телефон:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "preview_caption": (
            "📋 <b>ПРОСМОТР ЗАЯВКИ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>Ф.И.О.:</b> {name}\n"
            "👤 <b>Пол:</b> {sex}\n"
            "🎓 <b>Курс:</b> {level}-курс\n"
            "🏛 <b>Направление:</b> {faculty}\n"
            "📍 <b>Область:</b> {region}\n"
            "🏘 <b>Район:</b> {town}\n"
            "📝 <b>Причина:</b> {reason}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📞 <b>Доп. телефон:</b> {additional_phone}\n"
            "🆔 <b>Telegram:</b> @{username}\n"
            "🔗 <b>User ID:</b> {user_id}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "faq_title": "❓ <b>Часто задаваемые вопросы</b>\n",
        "faq_content": (
            "<b>1. Как подать заявку?</b>\n"
            "📝 Нажмите кнопку «Подать заявку» и заполните все данные.\n\n"
            "<b>2. Какие документы нужны?</b>\n"
            "📸 Фото основной страницы паспорта и фото формата 3x4.\n\n"
            "<b>3. Когда объявляются результаты?</b>\n"
            "📅 Результаты будут объявлены после сбора всех заявок.\n\n"
            "<b>4. Контакты:</b>\n"
            "📞 По дополнительным вопросам обращайтесь в университет."
        ),
        "other": "📌 Другое",
        "level_year": "{n}-курс",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Get translated text by key and language, with optional formatting."""
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
