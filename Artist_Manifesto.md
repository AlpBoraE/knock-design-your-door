# Artist Manifesto

## 1. Why This Medium?

I chose an interactive web artwork because the idea of a door is not only something to look at. A door asks for action. It waits for a hand, a pause, a decision, and sometimes a small amount of courage. A static poster could show a beautiful door, but it would not let the viewer bring their own threshold into the work. By using a website, I can invite the user to answer questions and make the door personal.

The medium also fits the subject of artificial intelligence. AI is often shown as something fast, efficient, and technical. I wanted to use it in a slower way. The user writes about something they left behind, the threshold they face now, and what they hope to hear if they knocked on a final or sacred door. The system does not give advice. It listens, reads the tone, and creates a poetic response. The screen becomes a place between confession, archive, and image. That slowness matters to me because the song itself does not rush its feeling. It lingers in a narrow space between fear and release.

This medium lets text, history, and visual imagination meet in one experience. The backend works like a hidden studio. The frontend works like the door itself.

## 2. What Caught Me?

What caught me first was the simplicity of the phrase "knocking on a door." It is an everyday action, but it can become very large when the door represents death, change, forgiveness, or the unknown. The song connected to this project has a plain emotional force. I did not want to copy that force or use the lyrics. I wanted to understand why the image of knocking still feels meaningful.

I was also caught by the year 1973. It is not only a date in music history. It is a time of war fatigue, protest, film, and cultural change. The United States was moving through the Vietnam War period, and many people were questioning authority, violence, and the future. At the same time, Pat Garrett & Billy the Kid gives us a western world where old legends are ending. Dust, badges, sunsets, and silence become signs of farewell.

These materials made me think about personal transition differently. A personal goodbye can feel private, but it often belongs to a larger world. When one person leaves home, finishes a stage of life, loses someone, or begins again, they are also touching old human themes: mortality, memory, legacy, and meaning.

## 3. AI as Tool, Collaborator, and Mirror

In this project, AI has three roles. First, it is a tool. It performs sentiment analysis, reads input, and generates structured output. This part is practical and clear. The system needs to classify emotional tone and respond in a predictable format so the artwork can function.

Second, AI is a collaborator. The language model can combine the user's words with the historical context and produce a new poetic text. I give it rules: do not quote lyrics, keep the door central, connect the personal answers to 1973, war, western imagery, farewell, and meaning. Within those limits, the model can make connections that feel surprising. It can turn a simple answer into an image with atmosphere.

Third, AI is a mirror. The emotional tone detection is not a perfect truth about the user. It is an interpretation. That matters because art also interprets us. If the system says the tone is melancholic, hopeful, angry, nostalgic, peaceful, or conflicted, the user can agree or disagree. The result can make the user notice something in their own language. In this way, the AI does not replace self-reflection. It gives the user another surface to reflect against.

The fallback generator is also important. If there is no API key, the project still works. This keeps the artwork accessible and honest. The AI parts are stronger with a language model and image model, but the concept does not disappear without them.

I think this matters for a course project as well. It is easy to use AI in a decorative way and claim that the result is deep just because it sounds poetic or looks cinematic. I wanted to avoid that trap. My goal was to build a system where each AI component had a clear role and where I could explain why it was there. The sentiment module is there to listen for emotional direction. The context retrieval is there to stop the historical material from becoming random wallpaper. The motif extractor is there to show how a user’s own words become symbols. The language model, when used, is there to connect these layers into a reflective whole. This structure helped me feel that I was not hiding behind AI. I was using it deliberately.

## 4. Historical Context: 1973, War, and Farewell

The historical context gives the project weight. Bob Dylan's 1973 connection to Pat Garrett & Billy the Kid places the song's atmosphere inside a western story about aging, death, friendship, and the end of a mythic world. The film is not just a cowboy story for this project. It becomes a landscape of transition. Pat Garrett represents law, compromise, and survival. Billy the Kid represents youth, rebellion, and legend. Their conflict feels like a door between two eras.

The Vietnam War era adds another kind of threshold. By 1973, the war had created deep grief and distrust. The counterculture anti-war movement showed that art, music, posters, and protest could become ways of refusing silence. Many people were asking what authority meant, what violence had cost, and what kind of future could still be imagined.

I use these contexts through symbols rather than direct explanation. A fallen badge suggests authority losing certainty. Dust suggests time, travel, and the body returning to the earth. Anti-war posters suggest public grief and resistance. Sunset suggests farewell, but it also means the day is not completely dark yet. The door holds all of these signs together.

The goal is not to make the user's life the same as 1973. That would be too simple. The goal is to place the user's personal threshold beside a historical atmosphere where many people were also asking how to continue.

## 5. My Door

My door is not a perfect golden gate. It is a weathered wooden door standing in a dusty western landscape. It has marks, shadows, and silence. Near it there are posters from an anti-war moment, a badge on the ground, and warm sunset light. The door is central because it is the place where the user must pause.

For me, the door represents the moment before change becomes real. Many transitions are not dramatic from the outside. A person may simply move, graduate, end a relationship, leave a childhood version of themselves, or accept that something cannot return. But inside, that moment can feel like standing before a huge door.

The questions in the project are designed to make that door personal. "What did you leave behind?" asks the user to name loss. "What threshold are you standing before?" asks the user to name the present. "What would you hope to hear?" asks the user to imagine permission, comfort, truth, or silence. The generated manifesto then turns those answers into a small ritual text.

The door belongs to the user, but it is also connected to history. This is why the result includes both personal language and cultural images from 1973.

I also realized while building the project that the door is not only about death, even though the song carries mortality very strongly. The door can also mean adulthood, leaving a family role, speaking after a long silence, or accepting that uncertainty will not disappear before action begins. That made the project more meaningful to me. It allowed me to treat the phrase "knocking on heaven’s door" not only as an image of finality, but also as an image of vulnerability. To knock is to admit that you do not fully control what happens next. That emotional honesty is part of what I wanted the work to preserve.

## 6. Technical and Creative Process

The technical process is simple enough to explain in a student presentation. The frontend is built with HTML, CSS, and vanilla JavaScript. The visual style uses a dark cinematic background, warm sunset tones, and a door-shaped panel, so the interface feels like part of the artwork.

The backend is built with FastAPI. When the user submits answers, the backend combines them into one text and sends the text to the sentiment module. That module uses VADER sentiment analysis with extra keyword signals to classify the emotional tone. Then the context loader reads three text files about Dylan in 1973, Vietnam counterculture, and Pat Garrett & Billy the Kid, and it scores smaller historical lenses. Those lenses are shown in the result. I also added a symbolic motif extractor, so the user can see which symbols came from their own answers.

After that, the generator creates a structured prompt for the language model. If a Gemini or OpenAI API key is available, it asks the model to write the manifesto, image prompt, and historical influence explanation. If the key is missing or the API call fails, a local fallback generator creates meaningful output from templates. The image generator is also optional. It can create and save an image if OpenAI image generation is available. If not, the app still shows the image prompt.

Every result is saved as a timestamped JSON file, which makes the process transparent.

That transparency became more important to me over time. I did not want the project to feel like a black box that magically outputs emotion and philosophy. Saving outputs, showing motifs, and showing historical lenses are small design choices, but they support trust. They let a reviewer see that the system is making traceable decisions. They also help me defend the project as original work, because the pipeline is visible and explainable instead of hidden behind a single API call.

## 7. Conclusion

KNOCK attempts to make AI feel reflective instead of impressive. The project uses several AI and NLP techniques: emotion analysis, context retrieval, symbolic motif extraction, contextual language generation, and image prompt or image generation. But the main point is the experience of turning a personal threshold into a symbolic door.

The project is inspired by a song, a film, and a historical moment, but it does not try to copy them. It uses their atmosphere: farewell, mortality, western dust, protest, silence, and the need to find meaning when one world is ending. The user brings the final missing part. Their answers decide what the door carries. In that sense, each run of the project becomes a different door, but the emotional and historical frame stays recognizable.

For me, this is why the web medium works well. The user does not only observe the artwork. They knock. The system answers with text, image, and context. The result is not a final truth, but a moment of attention. It asks what we leave behind, what we face now, and what voice we hope might meet us.
