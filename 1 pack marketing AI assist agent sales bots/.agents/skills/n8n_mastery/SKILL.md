# n8n Mastery Skill
# n8n Mastery: Community-Proven Expert Rules

## 🏗️ Architecture & Clean Flow
- **Modularization**: Break large flows into sub-workflows using the `Execute Workflow` node.
- **Early Filtering**: Strip unnecessary data as early as possible to save memory.
- **Explicit Processing**: Use `SplitInBatches` for datasets > 500 items to avoid memory spikes.
- **Documentation**: ALL complex logic MUST have a Sticky Note explaining "Why" it's done this way.
- **Error Resilience**: 
  - Enable `Retry on Fail` for all external API nodes.
  - Implementation of a `Global Error Workflow` for centralized logging/notifications.

## 🛡️ WhatsApp & Evolution API Anti-Ban (Expert Level)
- **Human Simulation**:
  - Implement `Typing` state before sending.
  - Use random delays (jitter) between messages, not just a fixed wait.
- **Logging Masking**: Configure Evolution instance to report as "Chrome/Windows" to avoid "Automation detected" flags.
- **Gradual Warmup**: Never send massive batches on day one. Increase volume by 10-15% daily.
- **Engagement Loop**: Periodically check for incoming messages and "Mark as Read" to simulate a real user.
- **Rate Limiting**: Add delays even for non-sending operations (like JID lookups) to avoid account flagging.

## 🛠️ Data Integrity
- **DataTable Schema**: Always verify columns exist before insertion using a `DataTable` GET node if unsure.
- **Unique Constraints**: Check JID presence in DB before every insertion to prevent duplicates.
