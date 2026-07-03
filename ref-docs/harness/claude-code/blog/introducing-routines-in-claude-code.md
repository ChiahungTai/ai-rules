Introducing routines in Claude Code | Claude by Anthropic
Explore here
Introducing routines in Claude Code
Define repeatable routines that work your backlog, review your PRs, and respond to events in the cloud.
Category
Product announcements
Product
Claude Code
Date
April 14, 2026
Reading time
5
min
Share
Copy link
https://claude.com/blog/introducing-routines-in-claude-code
Today, we're introducing routines in Claude Code in research preview. A routine is a Claude Code automation you configure once — including a prompt, repo, and connectors — and then run on a schedule, from an API call, or in response to an event. Routines run on Claude Code’s web infrastructure, so nothing depends on your laptop being open.
Developers already use Claude Code to automate the software development cycle, but until now, they've managed cron jobs, infrastructure, and additional tooling like MCP servers themselves. Routines ship with access to your repos and your connectors, so you can package up automations and set them to run on a schedule or trigger.
How it works
Scheduled routines
Give Claude Code a prompt and a cadence (hourly, nightly, or weekly) and it runs on that schedule:
Every night at 2am: pull the top bug from Linear, attempt a fix, and open a draft PR.
If you're using /schedule in the CLI, those tasks are now scheduled routines.
API routines
You can also configure routines to be triggered by API calls. Every routine gets its own endpoint and auth token. POST a message, get back a session URL. Wire Claude Code into your alerting, your deploy hooks, your internal tools—anywhere you can make an HTTP request:
Read the alert payload, find the owning service, and post a triage summary to #oncall with a proposed first step.
Webhook routines, starting with GitHub
Subscribe a routine to automatically kick off in response to GitHub repository events. Claude will create a new session for every PR matching your filters and run your routine.
Please flag PRs that touch the /auth-provider module. Any changes to this module need to be summarized and posted to #auth-changes.
Claude opens one session per PR and will continue to feed updates from that PR to the session, so it can address follow-ups like comments and CI failures.
We plan to expand webhook-based routines to trigger from more event sources in the future.
What teams are building
A few common patterns have emerged for early users creating routines:
Scheduled routines
Backlog management: triage new issues nightly, label, assign, and post a summary to Slack
Docs drift: scan merged PRs weekly, flag docs that reference changed APIs, and open update PRs
API routines
Deploy verification: your CD pipeline posts after each deploy, Claude runs smoke checks against the new build, scans error logs for regressions, and posts a go/no-go to the release channel
Alert triage: point Datadog at the routine's endpoint, Claude pulls the trace, correlates it with recent deployments, and has a draft fix waiting before on-call opens the page
Feedback resolution: a docs feedback widget or internal dashboard posts the report, Claude opens a session against the repo with the issue in context, and drafts the change
GitHub routines
Library port: every PR merged to a Python SDK triggers a routine that ports the change to the parallel Go SDK, and opens a matching PR
Bespoke code review: on PR opened, run your team's own checklist across security and performance, leaving inline comments before a human reviewer looks
Getting started
Routines are available today for Claude Code users on Pro, Max, Team, and Enterprise plans with Claude Code on the web enabled. Head to claude.ai/code to create your first routine, or type /schedule in the CLI.
Routines draw down subscription usage limits in the same way as interactive sessions. In addition, routines have daily limits: Pro users can run up to 5 routines per day, Max users can run up to 15 routines per day, and Team and Enterprise users can run up to 25 routines per day. You can run extra routines beyond these limits with extra usage. See the docs for more information.
No items found.
PrevPrev
0/5
NextNext
eBook
FAQ
No items found.
Get Claude Code
curl -fsSL https://claude.ai/install.sh | bash
Copy command to clipboard
irm https://claude.ai/install.ps1 | iex
Copy command to clipboard
Or read the documentation
Try Claude Code
Try Claude CodeTry Claude Code
Developer docs
Developer docsDeveloper docs
Related posts
Explore more product news and best practices for teams building with Claude.
Jul 2, 2026
Giving admins more visibility and control over Claude spend
Product announcements
Giving admins more visibility and control over Claude spendGiving admins more visibility and control over Claude spend
Giving admins more visibility and control over Claude spendGiving admins more visibility and control over Claude spend
Jun 29, 2026
Introducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Product announcements
Introducing the Claude apps gateway for Amazon Bedrock and Google CloudIntroducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Introducing the Claude apps gateway for Amazon Bedrock and Google CloudIntroducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Jun 29, 2026
Claude in Microsoft Foundry is now generally available
Product announcements
Claude in Microsoft Foundry is now generally availableClaude in Microsoft Foundry is now generally available
Claude in Microsoft Foundry is now generally availableClaude in Microsoft Foundry is now generally available
Jun 17, 2026
Secure access to the Claude Platform with Workload Identity Federation
Product announcements
Secure access to the Claude Platform with Workload Identity FederationSecure access to the Claude Platform with Workload Identity Federation
Secure access to the Claude Platform with Workload Identity FederationSecure access to the Claude Platform with Workload Identity Federation
Transform how your organization operates with Claude
See pricing
See pricingSee pricing
Contact sales
Contact salesContact sales
Get the developer newsletter
Product updates, how-tos, community spotlights, and more. Delivered monthly to your inbox.
Thank you! You’re subscribed.
Sorry, there was a problem with your submission, please try again later.
HomepageHomepage
Thank you! Your submission has been received!
Oops! Something went wrong while submitting the form.
Write
Button TextButton Text
Learn
Button TextButton Text
Code
Button TextButton Text
Write
Help me develop a unique voice for an audience
Hi Claude! Could you help me develop a unique voice for an audience? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Improve my writing style
Hi Claude! Could you improve my writing style? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Brainstorm creative ideas
Hi Claude! Could you brainstorm creative ideas? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Learn
Explain a complex topic simply
Hi Claude! Could you explain a complex topic simply? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Help me make sense of these ideas
Hi Claude! Could you help me make sense of these ideas? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Prepare for an exam or interview
Hi Claude! Could you prepare for an exam or interview? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Code
Explain a programming concept
Hi Claude! Could you explain a programming concept? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Look over my code and give me tips
Hi Claude! Could you look over my code and give me tips? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Vibe code with me
Hi Claude! Could you vibe code with me? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
More
Write case studies
This is another test
Write grant proposals
Hi Claude! Could you write grant proposals? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to — like Google Drive, web search, etc. — if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can - an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Write video scripts
this is a test
AnthropicAnthropic
© [year] Anthropic PBC
Products
Claude
ClaudeClaude
Claude Code
Claude CodeClaude Code
Claude Code for Enterprise
Claude Code for EnterpriseClaude Code for Enterprise
Claude Cowork
Claude CoworkClaude Cowork
@Claude
@Claude@Claude
Claude Design
Claude DesignClaude Design
Claude Science
Claude ScienceClaude Science
Claude Security
Claude SecurityClaude Security
Download app
Download appDownload app
Pricing
PricingPricing
Log in
Log inLog in
Features
Claude for Chrome
Claude for ChromeClaude for Chrome
Claude for Microsoft 365
Claude for Microsoft 365Claude for Microsoft 365
Skills
SkillsSkills
Models
Mythos
MythosMythos
Fable
FableFable
Opus
OpusOpus
Sonnet
SonnetSonnet
Haiku
HaikuHaiku
Solutions
AI agents
AI agentsAI agents
Code modernization
Code modernizationCode modernization
Coding
CodingCoding
Customer support
Customer supportCustomer support
Education
EducationEducation
Enterprise
EnterpriseEnterprise
Financial services
Financial servicesFinancial services
Government
GovernmentGovernment
Healthcare
HealthcareHealthcare
Legal
LegalLegal
Life sciences
Life sciencesLife sciences
Nonprofits
NonprofitsNonprofits
Security
SecuritySecurity
Small business
Small businessSmall business
Claude Platform
Overview
OverviewOverview
Developer docs
Developer docsDeveloper docs
Pricing
PricingPricing
Ecosystem
EcosystemEcosystem
Marketplace
MarketplaceMarketplace
Claude on AWS
Claude on AWSClaude on AWS
Google Cloud
Google CloudGoogle Cloud
Microsoft Foundry
Microsoft FoundryMicrosoft Foundry
Regional compliance
Regional complianceRegional compliance
Console login
Console loginConsole login
Resources
Blog
BlogBlog
Claude partner network
Claude partner networkClaude partner network
Community
CommunityCommunity
Connectors
ConnectorsConnectors
Courses
CoursesCourses
Customer stories
Customer storiesCustomer stories
Engineering at Anthropic
Engineering at AnthropicEngineering at Anthropic
Events
EventsEvents
Plugins
PluginsPlugins
Powered by Claude
Powered by ClaudePowered by Claude
Service partners
Service partnersService partners
Tutorials
TutorialsTutorials
Use cases
Use casesUse cases
Company
Anthropic
AnthropicAnthropic
Careers
CareersCareers
Policy
PolicyPolicy
Economic Futures
Economic FuturesEconomic Futures
Research
ResearchResearch
News
NewsNews
Policy on the AI Exponential
Policy on the AI ExponentialPolicy on the AI Exponential
Responsible Scaling Policy
Responsible Scaling PolicyResponsible Scaling Policy
Security and compliance
Security and complianceSecurity and compliance
Transparency
TransparencyTransparency
Programs
Startups
StartupsStartups
Research Labs
Research LabsResearch Labs
Help and security
Availability
AvailabilityAvailability
Status
StatusStatus
Support center
Support centerSupport center
Terms and policies
Privacy choices
Cookie settings
We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.
Customize cookie settings
Reject all cookies
Accept all cookies
Save preferences
Privacy policy
Privacy policyPrivacy policy
Responsible disclosure policy
Responsible disclosure policyResponsible disclosure policy
Terms of service: Commercial
Terms of service: CommercialTerms of service: Commercial
Terms of service: Consumer
Terms of service: ConsumerTerms of service: Consumer
Usage policy
Usage policyUsage policy
x.comx.com
LinkedInLinkedIn
YouTubeYouTube
InstagramInstagram
English (US)
Claude Code
Coding
Work
Productivity
Agents
