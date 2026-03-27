# ML-подпроект (ml)

Этот каталог содержит код OOTDiffusion и вспомогательные инструменты для виртуальной примерки одежды.

## Основные файлы

- **.gitignore** — список файлов и папок, которые игнорируются Git внутри подпроекта `ml`.
- **LICENSE** — лицензия, определяющая условия использования и распространения кода и моделей.
- **ML_System_Design_Doc_Template.md** — шаблон для документирования архитектурных решений и дизайна ML-системы.
- **README.md** — основной README проекта OOTDiffusion с инструкциями по установке и запуску.
- **requirements.txt** — основной список зависимостей для запуска кода OOTDiffusion.
- **requirements-ci.txt** — зависимости для CI, используемые при автоматическом тестировании.
- **download_models.py** — скрипт для скачивания необходимых предобученных моделей и контрольных точек.
- **ootd_service.py** — адаптер для использования ML-пайплайна из backend.

## Папка `images/`

- **demo.png** — пример результата работы модели.
- **workflow.png** — схема рабочего процесса и компонентов.

## Папка `ootd/` (ядро модели)

- **inference_ootd.py** — скрипт для запуска инференса модели в стандартном (half-body) сценарии.
- **inference_ootd_dc.py** — инференс для полного тела (Dress Code) с категорией одежды.
- **inference_ootd_hd.py** — инференс для модели высокой чёткости (HD).

### `oodt/pipelines_ootd/`

- **attention_garm.py** — модуль внимания для гардеробного (garment) потока.
- **attention_vton.py** — модуль внимания для общего VTON-потока.
- **pipeline_ootd.py** — главный класс пайплайна, связывающий все стадии обработки.
- **transformer_garm_2d.py** — 2D-трансформер для обработки данных гардероба.
- **transformer_vton_2d.py** — 2D-трансформер для VTON-процесса.
- **unet_garm_2d_blocks.py** — блоки U-Net для гардеробного потока.
- **unet_garm_2d_condition.py** — условная генерация для гардероба.
- **unet_vton_2d_blocks.py** — блоки U-Net для VTON-потока.
- **unet_vton_2d_condition.py** — условная генерация для VTON.

## `ootd_service.py`

Обёртка/сервис для запуска модели как инфраструктурного адаптера поверх `run/ootd_app`.

## Папка `preprocess/` (предобработка данных)

### `preprocess/humanparsing/` — сегментация человека и разметка частей тела

- **parsing_api.py** — обёртка/интерфейс для вызова процедуры парсинга.
- **run_parsing.py** — скрипт для запуска парсинга изображений и сохранения результатов.

#### `humanparsing/datasets/`

- **datasets.py** — классы для загрузки и подготовки данных.
- **simple_extractor_dataset.py** — упрощённый датасет для вырезания нужных частей.
- **target_generation.py** — генерация целевых меток/масок для обучения.

#### `humanparsing/mhp_extension/` — расширения для Multi-Human Parsing

- **logits_fusion.py** — слияние логитов от нескольких моделей/уровней.
- **make_crop_and_mask_w_mask_nms.py** — обрезка и генерация масок с NMS.

##### `mhp_extension/coco_style_annotation_creator/`

- **human_to_coco.py** — конвертация разметки человека в COCO-формат.
- **pycococreatortools.py** — утилиты для создания COCO-аннотаций.
- **test_human2coco_format.py** — тесты конвертации разметки.

##### `mhp_extension/global_local_parsing/`

- **global_local_datasets.py** — датасеты для глобального/локального подхода.
- **global_local_evaluate.py** — оценка качества парсинга.
- **global_local_train.py** — скрипт для обучения модели глобально/локально.
- **make_id_list.py** — генерация списков идентификаторов образцов.

##### `mhp_extension/scripts/`

- **make_coco_style_annotation.sh** — скрипт для создания COCO-разметки.
- **make_crop.sh** — скрипт для вырезания участков изображения.
- **parsing_fusion.sh** — скрипт для объединения результатов парсинга.

#### `humanparsing/modules/` — сборка модулей нейронных сетей

- **bn.py** — модули нормализации (BatchNorm) с расширениями.
- **deeplab.py** — реализация модели DeepLab для сегментации.
- **dense.py** — полносвязные слои и блоки.
- **functions.py** — вспомогательные функции (активации, нормализации и т.п.).
- **misc.py** — прочие утилиты и вспомогательные классы.
- **residual.py** — остаточные блоки (ResNet-подобные).
- **src/** — дополнительный исходный код и зависимости.

#### `humanparsing/networks/` — архитектуры

- **AugmentCE2P.py** — расширенная архитектура CE2P для парсинга.

##### `networks/backbone/`

- **mobilenetv2.py** — MobileNetV2 backbone.
- **resnet.py** — ResNet backbone.
- **resnext.py** — ResNeXt backbone.

##### `networks/context_encoding/`

- **aspp.py** — ASPP (Atrous Spatial Pyramid Pooling).
- **ocnet.py** — OCNet модуль.
- **psp.py** — PSPNet (Pyramid Scene Parsing).

#### `humanparsing/utils/` — утилиты для обучения и оценки

- **consistency_loss.py** — потеря консистентности между предсказаниями.
- **criterion.py** — критерии/функции потерь.
- **encoding.py** — кодирование/декодирование меток.
- **kl_loss.py** — KL-дивергенция.
- **lovasz_softmax.py** — функция потерь Lovasz-Softmax.
- **miou.py** — метрика mIoU для сегментации.
- **schp.py** — шаблоны для SCHP (Self-correction for Human Parsing).
- **soft_dice_loss.py** — потеря Soft Dice.
- **transforms.py** — трансформации для изображений и масок.
- **warmup_scheduler.py** — планировщик шага обучения с warmup.

### `preprocess/openpose/` — извлечение поз

- **run_openpose.py** — скрипт запуска OpenPose для извлечения поз.
- **annotator/** — модуль для аннотирования и визуализации поз.

## Папка `run/` — запуск модели и приложения

- **gradio_ootd.py** — запуск Gradio-интерфейса для демонстрации модели.
- **run_ootd.py** — основной скрипт запуска инференса OOTDiffusion.
- **utils_ootd.py** — вспомогательные функции для запуска и подготовки данных.

### `run/examples/`

- **garment/** — образцы одежды.
- **model/** — примеры путей к моделям и конфигурациям.

### `run/ootd_app/` — архитектура port/adapter (Clean Architecture)

- **adapters.py** — адаптеры для интеграции внешних компонентов.
- **entities.py** — сущности предметной области.
- **ports.py** — порты и интерфейсы для use case-ов.
- **usecases.py** — реализация бизнес-логики (use case) для приложения.

Поддерживаемые entrypoint'ы после очистки:

- backend вызывает `ml/ootd_service.py`
- CLI-инференс идёт через `run/run_ootd.py`
- demo остаётся в `run/gradio_ootd.py`

## Папка `tests/`

- **test_adapters_and_entry.py** — тесты адаптеров и точки входа в приложение.
- **test_gradio_module.py** — тесты Gradio-интерфейса.
- **test_usecase.py** — тесты отдельных use case-ов.
- **test_usecases.py** — интеграционные тесты сценариев использования.
- **test_utils_ootd.py** — тесты вспомогательных утилит для OOTDiffusion.
