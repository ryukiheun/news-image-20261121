-- Usage rows for the news-image-20261121 build + round-1 fix + round-2 fix sessions.
-- The query is the one bundle --help prints (step 1), with the model
-- joined in. Run it with the muse.db tool AFTER the sessions have
-- ended: Muse writes a message's usage row when the message is
-- delivered, and a session's row appears only once the session ends.
-- Queried 2026-11-22 ~17:35 KST, after all three sessions ended: 3 rows
-- (one per session — the delivered final-message usage row each).
SELECT u.agent_id AS agent_id, u.message_id AS message_id, u.created_at AS created_at, u.input_tokens AS input_tokens, u.output_tokens AS output_tokens, a.model AS model FROM agent.agent_message_token_usage u JOIN agent.agents a ON a.agent_id = u.agent_id WHERE u.agent_id IN ('311c5dce-a71b-47a5-a252-611e0c6c8be1', 'cf3c1d28-d139-4935-b577-64d9114e7a57', '82365aa9-3fed-4e59-a92e-316d0f712592') ORDER BY u.created_at DESC LIMIT 500
