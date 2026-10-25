# Image Handling

Part of the pdf-to-markdown skill. Load only this file for this topic.

Images are always extracted. They are:
1. **Cached** in `~/.cache/pdf-to-markdown/<cache_key>/images/`
2. **Copied** to `images/` folder next to the output `.md` file
3. **Referenced** in the markdown with relative paths (`images/filename.png`)
4. **Summarized** in a table at the end of the document

### Auto-View Behavior for Images

**IMPORTANT:** When the extracted markdown contains image references like:
```
**[Image: figure_1.png (1200x800, 125.3KB)]**
```

And the user asks about something that might be visual (charts, graphs, diagrams, figures, screenshots, layouts, designs, plots, illustrations), **automatically use the Read tool** to view the relevant image file(s) before answering. Don't ask the user - just look at it.

**Examples of when to auto-view images:**
- User: "What does the chart on page 3 show?" → Read the image file
- User: "Summarize the figures in this paper" → Read all image files
- User: "What's in the diagram?" → Read the image file
- User: "Describe the architecture shown" → Read the image file
- User: "What are the results?" (and there's a results figure) → Read it
