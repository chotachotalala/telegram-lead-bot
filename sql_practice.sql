-- 1. Найти заявки по услуге.
SELECT id, service, name, contact, created_at
FROM leads
WHERE service = 'Telegram-бот'
ORDER BY created_at DESC;


-- 2. Посчитать количество заявок по услугам.
SELECT service, COUNT(*) AS lead_count
FROM leads
GROUP BY service
ORDER BY lead_count DESC;


-- 3. Показать заявки вместе с Telegram-пользователями.
SELECT
    l.id,
    u.telegram_id,
    u.telegram_username,
    l.service,
    l.name,
    l.contact,
    l.created_at
FROM leads AS l
JOIN users AS u
    ON u.telegram_id = l.user_id
ORDER BY l.created_at DESC