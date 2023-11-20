init python:
    # Простой пример
    class SimpleAttributeImage:
        def __init__(self, *images):
            self.images = images
        
        def _duplicate(self, args):
            attributes = set(args.args)
            return Fixed(
                *(
                    renpy.easy.displayable(image_like) 
                    for attr, image_like in self.images
                    if attr in attributes
                ),
                xfit=True, yfit=True
            )

    # Простой пример
    class SimpleAttributeImageFix1:
        def __init__(self, *images):
            self.images = images
        
        def _duplicate(self, args):
            attributes = set(args.args)
            return Fixed(
                *(
                    renpy.easy.displayable(image_like) 
                    for attr, image_like in self.images
                    if attr in attributes
                ),
                xfit=True, yfit=True
            )
        
        def _choose_attributes(self, tag, required, optional):
            return tuple(required) + tuple(optional or [])
    
    # Пример с сохранением аттрибутов и исключением конфликтов
    class SimpleAttributeImageFix2:
        def __init__(self, *layers):
            self.layers = layers

        def _duplicate(self, args):
            selected = set(args.args)
            fixed = Fixed(xfit=True, yfit=True)
            for layer in self.layers:
                for attr, image_like in layer:
                    if attr in selected:
                        fixed.add(renpy.easy.displayable(image_like))
                        break
            
            return fixed

        def _choose_attributes(self, tag, required, optional):
            required_set = set(required)
            optional_set = set(optional) if optional is not None else set()
            conflicts = []

            def process_layer(layer):
                layer_selected = [
                    attr for attr, _ in layer if attr in required_set
                ]
                if len(layer_selected) > 1:
                    conflicts.extend(layer_selected)
                elif len(layer_selected) == 1:
                    for attr, _ in layer:
                        optional_set.discard(attr)

            for layer in self.layers:
                process_layer(layer)
            
            if conflicts:
                raise Exception('Attribute conflict: {0}'.format(conflicts))

            return tuple(required_set | optional_set)
    
    # Пример заточенный конкретно под определённый шаблон
    class ESSprite(python_object):
        def __init__(self, template, emotions, outfits):
            """
            :param str template: Шаблон вида "path/to/char/char_{body_number}_{image}.png"
            :emotions list[list[str]]: Двумерный список с набором атрибутов. Из этого списка будет составлена карта для определения номера позы
            :outfits list[str]: Список доступных нарядов
            """
            self.template = template
            self.emotion_to_body_index = {
                emotion: i for i, emotion_layer in enumerate(emotions) for emotion in emotion_layer
            }
            self.outfits = set(outfits)
        
        def _duplicate(self, args):
            emotion, body_index = None, 0
            outfit = None
            for attr in args.args:
                # Если атрибут эмоция, то находим индекс позы и запоминаюм эмоцию
                if attr in self.emotion_to_body_index:
                    emotion = attr
                    body_index = self.emotion_to_body_index[emotion]
                # Запоминаем наряд
                elif attr in self.outfits:
                    outfit = attr

            images = []
            
            def format(image):
                return self.template.format(image=image, body_number=body_index + 1)
            
            def add(image):
                if image is None:
                    return
                images.append(format(image))
            
            add('body')
            add(outfit)
            add(emotion)

            return Fixed(*images, xfit=True, yfit=True)

        def _choose_attributes(self, tag, required, optional):
            optional = list(optional) if optional else []

            outfit = None
            emotion = None
            conflicts = set()
            for attr in required:
                if attr in self.emotion_to_body_index:
                    # Если эмоция уже определена, то значит у нас конфликт атрибутов
                    if emotion:
                        conflicts.add(emotion)
                        conflicts.add(attr)
                    emotion = attr
                elif attr in self.outfits:
                    # Если наряд уже определён, то значит у нас конфликт атрибутов
                    if outfit:
                        conflicts.add(outfit)
                        conflicts.add(attr)
                    outfit = attr
            
            if conflicts:
                raise Exception('Attribute conflict: %s' % conflicts)
            
            # Выкидываем уже существущие атрибуты, если они конфликтуют с новыми
            if emotion:
                optional = [attr for attr in optional if attr not in self.emotion_to_body_index]
            if outfit:
                optional = [attr for attr in optional if attr not in self.outfits]
            
            return tuple(required) + tuple(optional)

        def _list_attributes(self, tag, attributes):
            attributes = attributes or []

            emotion = None
            outfit = None
            for attr in attributes:
                if attr in self.emotion_to_body_index:
                    emotion = attr
                elif attr in self.outfits:
                    outfit = attr
            
            result = []
            if emotion:
                result.append(emotion)
            else:
                result.extend(self.emotion_to_body_index)
            if outfit:
                result.append(outfit)
            else:
                result.extend(self.outfits)
            
            return result

                

image example1 = SimpleAttributeImage(
    ('base', 'images/simple/base.png'),
    ('smile', 'images/simple/smile.png'),
    ('serious', 'images/simple/serious.png'),
    ('normal', 'images/simple/normal.png')
)

image example2 = SimpleAttributeImageFix1(
    ('base', 'images/simple/base.png'),
    ('smile', 'images/simple/smile.png'),
    ('serious', 'images/simple/serious.png'),
    ('normal', 'images/simple/normal.png')
)

image example3 = SimpleAttributeImageFix2(
    [('base', 'images/simple/base.png')],
    [('smile', 'images/simple/smile.png'), ('serious', 'images/simple/serious.png'), ('normal', 'images/simple/normal.png')],
    [('pioneer', 'images/simple/pioneer.png'), ('dress', 'images/simple/dress.png')]
)

image example4 = SimpleAttributeImageFix2(
    [('base1', 'images/simple/base.png'), ('base2', 'images/simple/base2.png')],
    [('smile', 'images/simple/smile.png'), ('serious', 'images/simple/serious.png'), ('normal', 'images/simple/normal.png'), ('happy', 'images/simple/happy.png')],
    [('pioneer', 'images/simple/pioneer.png'), ('dress', 'images/simple/dress.png')]
)

image example5 = ESSprite(
    template='images/sprites/sl/sl_{body_number}_{image}.png',
    emotions=[
        ['normal', 'serious', 'smile'],
        ['happy', 'laugh', 'smile2', 'shy'],
        ['angry', 'sad', 'surprise'],
        ['scared', 'tender']
    ],
    outfits=['swim', 'dress', 'pioneer', 'sport']
)


screen exception_message(ex):
    frame:
        xalign .5
        yalign .5
        text '[ex!q]' color '#a00'

init python:
    def dumb_format_function(what, name, group, variant, attribute, image, image_format, **kwargs):
        if image is None:
            image = attribute
        return Text(image)

layeredimage girl:
    format_function dumb_format_function

    always "body"
    group outfit:
        attribute swim
        attribute dress
        attribute sleep
    group emotion:
        attribute smile
        attribute cry
        attribute sad


init python:
    config.scene_callbacks.append(lambda *args: renpy.show('ext_beach_day'))


label start:
    scene
    show example1 base smile as first at left
    show example1 base serious as second at center
    show example1 base normal as third at right

    'Выглядит отлично!'

    hide second
    show example1 serious as first
    show example1 base smile serious normal as third

    'Или нет...'

    scene
    show example2 base smile
    'Улыбается.'
    show example2 serious
    '№#&@$@$Y@#@#@?'

    scene
    show example3 base normal
    'База.'
    show example3 dress
    'Смена наряда.'
    show example3 smile
    'Смена эмоции.'
    python:
        try:
            renpy.show('example3 dress pioneer')
        except Exception as e:
            renpy.say(None, '[e!q]', what_color='#a00')

    scene
    show example4 base2 happy
    'Пока всё нормально.'
    show example4 base1 dress
    'Сукуна пытается отобрать тело у Слави?'

    scene
    show example5 dress smile
    'dress smile'
    show example5 laugh
    'dress laugh'
    show example5 sport
    'sport laugh' 
    show example5 -sport
    'laugh' 
    show example5 -laugh
    ''
    python:
        try:
            renpy.show('example5 dress pioneer sport smile laugh happy tender')
        except Exception as e:
            renpy.say(None, '[e!q]', what_color='#a00')

    scene
    show ext_camp_entrance_day
    show example5 dress happy at left as left
    show example5 sport tender at center as center
    show example5 serious pioneer at right as right
    '...'

    return