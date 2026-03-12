Этот каталог содержит код OOTDiffusion и вспомогательные инструменты для виртуальной примерки одежды.

.gitignore - Список файлов и папок, которые игнорируются Git внутри подпроекта ml.

LICENSE - Лицензия, определяющая условия использования и распространения кода и моделей.

ML_System_Design_Doc_Template.md - Шаблон для документирования архитектурных решений и дизайна ML-системы.

README.md - Основной README проекта OOTDiffusion с инструкциями по установке и запуску.

download_models.py - Скрипт для скачивания необходимых предобученных моделей и контрольных точек (checkpoints).

images/ - Папка с примерами изображений, скриншотами демонстраций и диаграммами рабочего процесса.

  demo.png - Пример результата работы модели.
  workflow.png - Схема рабочего процесса и компонентов.

ootd/ - Основной код модели OOTDiffusion, включающий инфраструктуру инференса и архитектуру сети.

  inference_ootd.py - Скрипт для запуска инференса модели по стандартному сценарию (half-body).
  inference_ootd_dc.py - Скрипт инференса для полного тела (Dress Code, DC) с категорией одежды.
  inference_ootd_hd.py - Скрипт инференса для модели высокой чёткости (HD).

  pipelines_ootd/ - Реализации пайплайнов и архитектурных блоков OOTDiffusion.
    attention_garm.py - Модуль внимания для гардеробного (garment) потока.
    attention_vton.py - Модуль внимания для общего VTON-потока.
    pipeline_ootd.py - Главный класс пайплайна, связывающий все стадии обработки.
    transformer_garm_2d.py - 2D-трансформер для обработки данных гардероба.
    transformer_vton_2d.py - 2D-трансформер для VTON-процесса.
    unet_garm_2d_blocks.py - Блоки U-Net для гардеробного потока.
    unet_garm_2d_condition.py - Условия и модули условной генерации для гардероба.
    unet_vton_2d_blocks.py - Блоки U-Net для VTON-потока.
    unet_vton_2d_condition.py - Условная генерация для VTON.

ootd_service.py - Обёртка/сервис для запуска модели как API (например, для веб-сервиса или сервера инференса).

preprocess/ - Инструменты для предварительной обработки данных: парсинг человека, извлечение позы и подготовка масок.

  humanparsing/ - Код для сегментации человека и разметки частей тела (human parsing).
    parsing_api.py - Обёртка/интерфейс для вызова процедуры парсинга.
    run_parsing.py - Скрипт для запуска парсинга изображений и сохранения результатов.

    datasets/ - Наборы данных и их загрузчики.
      datasets.py - Классы для загрузки и подготовки данных.
      simple_extractor_dataset.py - Упрощённый датасет для вырезания нужных частей.
      target_generation.py - Генерация целевых меток/масок для обучения.

    mhp_extension/ - Расширения для работы с Multi-Human Parsing (MHP).
      logits_fusion.py - Слияние логитов от нескольких моделей/уровней.
      make_crop_and_mask_w_mask_nms.py - Обрезка и генерация масок с NMS.

      coco_style_annotation_creator/ - Утилиты для конвертации разметки в формат COCO.
        human_to_coco.py - Конвертация разметки человека в COCO-формат.
        pycococreatortools.py - Помощники для создания COCO-аннотаций.
        test_human2coco_format.py - Тесты конвертации разметки.

      global_local_parsing/ - Модули для схемы глобального и локального парсинга.
        global_local_datasets.py - Датасеты для глобального/локального подхода.
        global_local_evaluate.py - Оценка качества парсинга.
        global_local_train.py - Скрипт для обучения модели глобально/локально.
        make_id_list.py - Генерация списков идентификаторов образцов.

      scripts/ - Утилиты-скрипты для подготовки данных.
        make_coco_style_annotation.sh - Скрипт для создания COCO-разметки.
        make_crop.sh - Скрипт для вырезания участков изображения.
        parsing_fusion.sh - Скрипт для объединения результатов парсинга.

    modules/ - Сборка основных модулей нейросетей.
      bn.py - Модули нормализации (BatchNorm) с расширениями.
      deeplab.py - Реализация модели DeepLab для сегментации.
      dense.py - Полносвязные слои и блоки.
      functions.py - Вспомогательные функции (активации, нормализации и т.п.).
      misc.py - Прочие утилиты и вспомогательные классы.
      residual.py - Остаточные блоки (ResNet-подобные).
      src/ - Дополнительный исходный код и зависимости.

    networks/ - Определения архитектур сетей и бэкбонов.
      AugmentCE2P.py - Расширенная архитектура CE2P для парсинга.
      backbone/ - Реализации Backbone-сетей.
        mobilenetv2.py - MobileNetV2 backbone.
        resnet.py - ResNet backbone.
        resnext.py - ResNeXt backbone.
      context_encoding/ - Модули контекстного кодирования.
        aspp.py - ASPP (Atrous Spatial Pyramid Pooling).
        ocnet.py - OCNet модуль.
        psp.py - PSPNet (Pyramid Scene Parsing).

    utils/ - Утилиты для обучения и оценки.
      consistency_loss.py - Потеря консистентности между предсказаниями.
      criterion.py - Критерии/функции потерь.
      encoding.py - Кодирование/декодирование меток.
      kl_loss.py - KL-дивергенция.
      lovasz_softmax.py - Функция потерь Lovasz-Softmax.
      miou.py - Метрика mIoU для сегментации.
      schp.py - Шаблоны для SCHP (Self-correction for Human Parsing).
      soft_dice_loss.py - Потеря Soft Dice.
      transforms.py - Трансформации для изображений и масок.
      warmup_scheduler.py - Планировщик шага обучения с warmup.

  openpose/ - Инструменты для извлечения скелетных ключевых точек (pose estimation).
    run_openpose.py - Скрипт запуска OpenPose для извлечения поз.
    annotator/ - Модуль для аннотирования и визуализации поз.

requirements-ci.txt - Зависимости Python, используемые в CI для проверки проекта.

requirements.txt - Основной список зависимостей для запуска кода OOTDiffusion.

run/ - Скрипты для запуска модели, веб-приложения и утилит.

  __init__.py - Маркер пакета Python.
  gradio_ootd.py - Запуск Gradio-интерфейса для демонстрации модели.
  run_ootd.py - Основной скрипт запуска инференса OOTDiffusion.
  utils_ootd.py - Вспомогательные функции для запуска и подготовки данных.

  examples/ - Примеры моделей и одежды (шаблоны) для быстрых запусков.
    garment/ - Образцы одежды.
    model/ - Примеры путей к моделям и конфигурациям.

  ootd_app/ - Приложение с архитектурой портов/адаптеров для clean-архитектуры.
    adapters.py - Адаптеры для интеграции внешних компонентов.
    entities.py - Сущности предметной области.
    ports.py - Порты и интерфейсы для use case-ов.
    usecases.py - Реализация бизнес-логики (use case) для приложения.

test_tryon.py - Быстрый скрипт для запуска проверки пайплайна виртуальной примерки.

tests/ - Набор тестов для проверки работоспособности и стабильности.
  test_adapters_and_entry.py - Тесты адаптеров и точки входа в приложение.
  test_gradio_module.py - Тесты Gradio-интерфейса.
  test_usecase.py - Тесты отдельных use case-ов.
  test_usecases.py - Интеграционные тесты сценариев использования.
  test_utils_ootd.py - Тесты вспомогательных утилит для OOTDiffusion.
