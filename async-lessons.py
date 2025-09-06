import asyncio
import random
import secrets
from time import perf_counter


async def fetch_data(name: str, delay: float) -> dict:
    # Simulate I/O waiting for delay
    await asyncio.sleep(delay)
    data = secrets.token_hex(16)
    print(f"{name} ok in {delay:.1f}s")
    return {"data": data}


# ===============================
#            Basic tasks
# ===============================


async def basic_tasks():
    init = perf_counter()

    # Execute 3 concurrent tasks (single-thread, cooperative)
    results = await asyncio.gather(
        fetch_data("A", 1.0),
        fetch_data("B", 2.0),
        fetch_data("C", 1.5),
    )

    # Wait for all tasks to complete

    duration = perf_counter() - init
    print(results)
    for result in results:
        print(f"Received result: {result}")
    print(f"Total: {duration:.2f}s (deveria ser ~2.0s, não 1.0+2.0+1.5)")


# ===============================
#            Task Groups
# ===============================


class TaskGroupExamples:
    """Demonstra diferentes cenários de uso do asyncio.TaskGroup."""

    @staticmethod
    async def basic_task_group():
        """Exemplo básico de TaskGroup com nomes aleatórios."""
        init = perf_counter()
        tasks = []

        async with asyncio.TaskGroup() as tg:
            # Criar listas e embaralhar aleatoriamente
            nomes = ["laranja", "macaco", "banana", "casa"]
            tempos = [1.0, 2.0, 1.5, 4.0]
            random.shuffle(nomes)

            for nome, sleep_time in zip(nomes, tempos, strict=False):
                task = tg.create_task(fetch_data(nome, sleep_time))
                tasks.append(task)

        results = [task.result() for task in tasks]
        print(f"📊 Resultados: {results}")
        for result in results:
            print(f"📋 Resultado recebido: {result}")

        duration = perf_counter() - init
        print(f"⏱️  Total: {duration:.2f}s (deveria ser ~4.0s, não 1.0+2.0+1.5+4.0)")
        return results

    @staticmethod
    async def task_group_with_error_handling():
        """TaskGroup com tratamento de erros e exceções."""
        init = perf_counter()
        print("\n🔄 TaskGroup com tratamento de erros...")

        async def fetch_with_retry(name: str, delay: float, fail_chance: float = 0.3):
            """Simula fetch com possibilidade de falha."""
            await asyncio.sleep(delay)
            if random.random() < fail_chance:
                raise Exception(f"Falha simulada para {name}")
            return {"data": f"Sucesso para {name}", "delay": delay}

        try:
            async with asyncio.TaskGroup() as tg:
                # Algumas tasks podem falhar
                tg.create_task(fetch_with_retry("A", 1.0, 0.1))
                tg.create_task(fetch_with_retry("B", 1.5, 0.5))
                tg.create_task(fetch_with_retry("C", 2.0, 0.2))
                tg.create_task(fetch_with_retry("D", 0.5, 0.8))

                print("🚀 Tasks criadas, aguardando conclusão...")

        except Exception as e:
            print(f"❌ Alguma task falhou: {e}")

        duration = perf_counter() - init
        print(f"⏱️  Tempo total: {duration:.2f}s")
        return duration

    @staticmethod
    async def task_group_with_timeout():
        """TaskGroup com timeout global para todas as tasks."""
        init = perf_counter()
        print("\n⏰ TaskGroup com timeout global...")

        try:
            async with asyncio.timeout(2.5):  # Timeout global de 2.5s
                async with asyncio.TaskGroup() as tg:
                    # Tasks com diferentes durações
                    tg.create_task(fetch_data("Rápida", 0.5))
                    tg.create_task(fetch_data("Média", 1.5))
                    tg.create_task(fetch_data("Lenta", 3.0))  # Vai falhar por timeout
                    tg.create_task(
                        fetch_data("Muito Lenta", 4.0),
                    )  # Vai falhar por timeout

                    print("🚀 Tasks criadas com timeout de 2.5s...")
                    await asyncio.sleep(0.1)  # Checkpoint para o cancellation scope

        except TimeoutError:
            print("⏰ Timeout global atingido! Algumas tasks foram canceladas.")

        duration = perf_counter() - init
        print(f"⏱️  Tempo total: {duration:.2f}s")
        return duration

    @staticmethod
    async def task_group_with_conditional_tasks():
        """TaskGroup que cria tasks condicionalmente baseado em resultados."""
        init = perf_counter()
        print("\n🎯 TaskGroup com tasks condicionais...")

        async def check_condition(name: str) -> bool:
            """Simula verificação de condição."""
            await asyncio.sleep(0.5)
            return random.choice([True, False])

        async def process_if_valid(name: str):
            """Processa apenas se a condição for válida."""
            await asyncio.sleep(1.0)
            return f"Processado: {name}"

        results = []
        async with asyncio.TaskGroup() as tg:
            # Primeira fase: verificar condições
            condition_tasks = []
            for name in ["Item1", "Item2", "Item3", "Item4"]:
                task = tg.create_task(check_condition(name))
                condition_tasks.append((name, task))

            # Segunda fase: processar apenas os válidos
            process_tasks = []
            for name, condition_task in condition_tasks:
                is_valid = await condition_task
                if is_valid:
                    print(f"✅ {name} é válido, criando task de processamento...")
                    process_task = tg.create_task(process_if_valid(name))
                    process_tasks.append(process_task)
                else:
                    print(f"❌ {name} não é válido, pulando...")

            # Coletar resultados
            for task in process_tasks:
                result = await task
                results.append(result)

        duration = perf_counter() - init
        print(f"📊 Resultados finais: {results}")
        print(f"⏱️  Tempo total: {duration:.2f}s")
        return results

    @staticmethod
    async def task_group_with_resource_limiting():
        """TaskGroup com limitação de recursos (semáforo)."""
        init = perf_counter()
        print("\n🔒 TaskGroup com limitação de recursos...")

        # Semáforo limita a 2 tasks simultâneas
        semaphore = asyncio.Semaphore(2)

        async def fetch_with_semaphore(name: str, delay: float):
            """Fetch com controle de recursos via semáforo."""
            async with semaphore:
                print(f"🔓 {name} adquiriu semáforo")
                await asyncio.sleep(delay)
                print(f"🔓 {name} liberou semáforo")
                return {"data": f"Dados de {name}", "delay": delay}

        results = []
        async with asyncio.TaskGroup() as tg:
            # Criar 6 tasks, mas apenas 2 podem rodar simultaneamente
            for i in range(6):
                task = tg.create_task(
                    fetch_with_semaphore(f"Task{i + 1}", 1.0 + i * 0.2),
                )
                results.append(task)

            print("🚀 6 tasks criadas com semáforo limitando a 2 simultâneas...")

        # Coletar resultados
        final_results = [task.result() for task in results]
        duration = perf_counter() - init
        print(f"📊 Resultados: {final_results}")
        print(f"⏱️  Tempo total: {duration:.2f}s")
        return final_results


async def task_groups():
    """Executa todos os exemplos de TaskGroup."""
    print("🚀 DEMONSTRANDO TASK GROUPS...")
    print("=" * 50)

    # Executar todos os exemplos
    await TaskGroupExamples.basic_task_group()
    await TaskGroupExamples.task_group_with_error_handling()
    await TaskGroupExamples.task_group_with_timeout()
    await TaskGroupExamples.task_group_with_conditional_tasks()
    await TaskGroupExamples.task_group_with_resource_limiting()

    print("=" * 50)
    print("✅ Todos os exemplos de TaskGroup concluídos!")


# ===============================
#            Future
# ===============================


class FutureSimulator:
    """Encapsula operações assíncronas para resolver ou falhar um Future."""

    @staticmethod
    async def set_result(future: asyncio.Future, result: str):
        """Simula uma operação assíncrona que resolve um Future."""
        await asyncio.sleep(2)
        future.set_result(result)
        print(f"✅ Future resolvido com resultado: '{result}'")

    @staticmethod
    async def set_exception(future: asyncio.Future, error_msg: str):
        """Simula uma operação que falha e define uma exceção no Future."""
        await asyncio.sleep(1.5)
        future.set_exception(Exception(error_msg))
        print(f"❌ Future falhou com exceção: '{error_msg}'")


class FutureDemoCases:
    """Encapsula demonstrações de uso de asyncio.Future."""

    @staticmethod
    async def demonstrate_basic_future_success(event_loop):
        """Demonstra um Future básico resolvido com sucesso."""
        print("\n📋 Caso 1: Future com resultado bem-sucedido")
        future_result = event_loop.create_future()
        resolve_task = event_loop.create_task(
            FutureSimulator.set_result(
                future_result,
                "Operação concluída com sucesso!",
            ),
        )
        print(f"Task 1: {resolve_task}")

        try:
            result_value = await future_result
            print(f"🎯 Resultado recebido: {result_value}")
        except Exception as exc:
            print(f"❌ Erro inesperado: {exc}")

    @staticmethod
    async def demonstrate_future_with_exception(event_loop):
        """Demonstra um Future que termina com exceção."""
        print("\n📋 Caso 2: Future com falha/exceção")
        future_result = event_loop.create_future()
        exception_task = event_loop.create_task(
            FutureSimulator.set_exception(
                future_result,
                "Erro de conexão com banco de dados",
            ),
        )
        print(f"Task 2: {exception_task}")

        try:
            result_value = await future_result
            print(f"🎯 Resultado recebido: {result_value}")
        except Exception as exc:
            print(f"❌ Exceção capturada: {exc}")

    @staticmethod
    async def demonstrate_future_with_timeout(event_loop):
        """Demonstra um Future que excede o tempo limite (timeout)."""
        print("\n📋 Caso 3: Future com timeout")
        future_result = event_loop.create_future()
        delayed_task = event_loop.create_task(
            FutureSimulator.set_result(future_result, "Resultado tardio"),
        )

        try:
            result_value = await asyncio.wait_for(future_result, timeout=1.0)
            print(f"🎯 Resultado recebido: {result_value}")
        except TimeoutError:
            print("⏰ Timeout! Future não foi resolvido a tempo")
            delayed_task.cancel()

    @staticmethod
    async def demonstrate_future_with_callback(event_loop):
        """Demonstra um Future com callback de conclusão."""
        print("\n📋 Caso 4: Future com callback de conclusão")
        future_result = event_loop.create_future()

        def on_future_done(completed_future):
            if completed_future.done():
                if completed_future.exception():
                    print(
                        f"🔔 Callback: Future falhou com {completed_future.exception()}",
                    )
                else:
                    print(
                        f"🔔 Callback: Future concluído com {completed_future.result()}",
                    )

        future_result.add_done_callback(on_future_done)
        callback_task = event_loop.create_task(
            FutureSimulator.set_result(future_result, "Future com callback!"),
        )
        print(f"Task 3: {callback_task}")
        await asyncio.sleep(0.1)

    @staticmethod
    async def demonstrate_multiple_futures_with_gather(event_loop):
        """Demonstra múltiplos Futures resolvidos em paralelo usando gather."""
        print("\n📋 Caso 5: Múltiplos Futures com gather")
        future_list = []
        for idx in range(3):
            future_result = event_loop.create_future()
            future_list.append(future_result)
            gather_task = event_loop.create_task(
                FutureSimulator.set_result(future_result, f"Resultado {idx + 1}"),
            )
            print(f"Task 4: {gather_task}")

        all_results = await asyncio.gather(*future_list, return_exceptions=True)
        print(f"🎯 Todos os futures resolvidos: {all_results}")
        return all_results


async def main_future():
    """Demonstra os benefícios e casos de uso do Future."""
    init = perf_counter()
    print("🚀 Demonstrando Futures em asyncio...")
    print("=" * 50)

    loop = asyncio.get_running_loop()

    await FutureDemoCases.demonstrate_basic_future_success(loop)
    await FutureDemoCases.demonstrate_future_with_exception(loop)
    await FutureDemoCases.demonstrate_future_with_timeout(loop)
    await FutureDemoCases.demonstrate_future_with_callback(loop)
    results = await FutureDemoCases.demonstrate_multiple_futures_with_gather(loop)

    duration = perf_counter() - init
    print(f"\n⏱️  Tempo total: {duration:.2f}s")
    print("=" * 50)

    demonstrate_future_benefits()
    return results


def demonstrate_future_benefits():
    """Explica por que usar Futures."""
    print("\n💡 BENEFÍCIOS DOS FUTURES:")
    print("1. Controle manual sobre quando e como resolver operações assíncronas")
    print("2. Possibilidade de cancelar operações em andamento")
    print("3. Tratamento de exceções personalizado")
    print("4. Callbacks para reações automáticas quando operações terminam")
    print("5. Timeouts configuráveis")
    print("6. Composição de múltiplas operações assíncronas")
    print("7. Separação entre criação e execução de operações")
    print("8. Útil para APIs que precisam de controle granular sobre operações")


# ===============================
#            Locks
# ===============================


class AsyncLockExamples:
    """Demonstra diferentes tipos de locks e sincronização em asyncio."""

    @staticmethod
    async def basic_lock_example():
        """Exemplo básico de Lock para acesso exclusivo a um recurso."""
        print("\n🔒 Exemplo básico de Lock...")

        # Recurso compartilhado
        shared_counter = 0
        lock = asyncio.Lock()

        async def increment_with_lock(name: str, delay: float):
            """Incrementa o contador com lock exclusivo."""
            nonlocal shared_counter
            async with lock:
                print(f"🔓 {name} adquiriu o lock")
                current = shared_counter
                await asyncio.sleep(delay)  # Simula trabalho
                shared_counter = current + 1
                print(f"🔓 {name} liberou o lock, contador: {shared_counter}")

        # Executar múltiplas tasks concorrentes
        async with asyncio.TaskGroup() as tg:
            tg.create_task(increment_with_lock("Task A", 0.5))
            tg.create_task(increment_with_lock("Task B", 0.3))
            tg.create_task(increment_with_lock("Task C", 0.7))
            tg.create_task(increment_with_lock("Task D", 0.2))

        print(f"📊 Contador final: {shared_counter}")
        return shared_counter

    @staticmethod
    async def rlock_example():
        """Exemplo de RLock (Reentrant Lock) para funções recursivas."""
        print("\n🔄 Exemplo de RLock (Reentrant Lock)...")

        rlock = asyncio.Lock()  # asyncio.Lock já é reentrant

        async def recursive_function(name: str, depth: int):
            """Função que chama a si mesma, demonstrando reentrância."""
            async with rlock:
                print(f"🔓 {name} nível {depth} - lock adquirido")
                if depth > 0:
                    await asyncio.sleep(0.1)
                    await recursive_function(name, depth - 1)
                print(f"🔓 {name} nível {depth} - lock liberado")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(recursive_function("Task A", 3))
            tg.create_task(recursive_function("Task B", 2))

        print("✅ RLock demonstrado com sucesso!")

    @staticmethod
    async def semaphore_example():
        """Exemplo de Semaphore para limitar concorrência."""
        print("\n🚦 Exemplo de Semaphore...")

        # Semáforo permite apenas 3 tasks simultâneas
        semaphore = asyncio.Semaphore(3)

        async def worker_with_semaphore(name: str, work_time: float):
            """Worker que usa semáforo para limitar concorrência."""
            async with semaphore:
                print(
                    f"🚦 {name} adquiriu semáforo (slots disponíveis: {semaphore._value})",
                )
                await asyncio.sleep(work_time)
                print(f"🚦 {name} liberou semáforo")
                return f"Trabalho de {name} concluído"

        # Criar 6 workers, mas apenas 3 podem rodar simultaneamente
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for idx in range(6):
                task = tg.create_task(
                    worker_with_semaphore(f"Worker{idx + 1}", 1.0 + idx * 0.2),
                )
                tasks.append(task)

        results = [task.result() for task in tasks]
        print(f"📊 Resultados: {results}")
        return results

    @staticmethod
    async def event_example():
        """Exemplo de Event para sincronização entre tasks."""
        print("\n🎯 Exemplo de Event...")

        # Event para sinalizar que uma condição foi atendida
        ready_event = asyncio.Event()
        results = []

        async def producer():
            """Producer que prepara dados e sinaliza quando pronto."""
            print("🏭 Producer iniciando preparação...")
            await asyncio.sleep(2.0)  # Simula preparação
            print("🏭 Producer sinalizando que está pronto!")
            ready_event.set()

        async def consumer(name: str):
            """Consumer que aguarda o producer estar pronto."""
            print(f"👤 {name} aguardando producer...")
            await ready_event.wait()
            print(f"👤 {name} recebeu sinal, processando...")
            await asyncio.sleep(0.5)
            results.append(f"Dados processados por {name}")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer())
            tg.create_task(consumer("Consumer A"))
            tg.create_task(consumer("Consumer B"))
            tg.create_task(consumer("Consumer C"))

        print(f"📊 Resultados: {results}")
        return results

    @staticmethod
    async def condition_example():
        """Exemplo de Condition para sincronização complexa."""
        print("\n🔐 Exemplo de Condition...")

        # Condition para coordenar acesso a um buffer
        condition = asyncio.Condition()
        buffer: list[str] = []
        max_size = 3

        async def producer_condition(name: str):
            """Producer que aguarda espaço no buffer."""
            for idx in range(3):
                async with condition:
                    # Aguardar até ter espaço no buffer
                    while len(buffer) >= max_size:
                        print(f"🏭 {name} aguardando espaço no buffer...")
                        await condition.wait()

                    item = f"Item{idx} de {name}"
                    buffer.append(item)
                    print(f"🏭 {name} adicionou {item}, buffer: {buffer}")
                    condition.notify()  # Notificar consumers

                await asyncio.sleep(0.3)

        async def consumer_condition(name: str):
            """Consumer que aguarda itens no buffer."""
            for idx in range(3):
                async with condition:
                    # Aguardar até ter itens no buffer
                    while len(buffer) == 0:
                        print(f"👤 {name} aguardando itens no buffer...")
                        await condition.wait()

                    item = buffer.pop(0)
                    print(f"👤 {name} consumiu {item}, buffer: {buffer}")
                    condition.notify()  # Notificar producers

                await asyncio.sleep(0.4)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer_condition("Producer A"))
            tg.create_task(consumer_condition("Consumer A"))

        print(f"📊 Buffer final: {buffer}")
        return buffer

    @staticmethod
    async def barrier_example():
        """Exemplo de Barrier para sincronização de múltiplas tasks."""
        print("\n🚧 Exemplo de Barrier...")

        # Barrier que aguarda 3 tasks chegarem
        barrier = asyncio.Barrier(3)

        async def worker_with_barrier(name: str, work_time: float):
            """Worker que aguarda todos chegarem na barrier."""
            print(f"👷 {name} iniciando trabalho...")
            await asyncio.sleep(work_time)
            print(f"👷 {name} chegou na barrier, aguardando outros...")

            try:
                await barrier.wait()
                print(f"🎉 {name} passou pela barrier! Todos chegaram!")
            except asyncio.BrokenBarrierError:
                print(f"❌ {name} - Barrier foi quebrada!")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(worker_with_barrier("Worker A", 0.5))
            tg.create_task(worker_with_barrier("Worker B", 1.0))
            tg.create_task(worker_with_barrier("Worker C", 1.5))

        print("✅ Barrier concluída com sucesso!")

    @staticmethod
    async def queue_example():
        """Exemplo de Queue para comunicação entre tasks."""
        print("\n📦 Exemplo de Queue...")

        # Queue para comunicação producer-consumer
        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=3)
        results = []

        async def producer_queue(name: str, items: int):
            """Producer que coloca itens na queue."""
            for i in range(items):
                item = f"Item{i} de {name}"
                await queue.put(item)
                print(f"🏭 {name} colocou {item} na queue (tamanho: {queue.qsize()})")
                await asyncio.sleep(0.2)

            # Sinalizar fim
            await queue.put(None)
            print(f"🏭 {name} finalizou")

        async def consumer_queue(name: str):
            """Consumer que retira itens da queue."""
            while True:
                item = await queue.get()
                if item is None:
                    queue.task_done()
                    break

                print(f"👤 {name} consumiu {item}")
                await asyncio.sleep(0.3)
                results.append(f"{name} processou {item}")
                queue.task_done()

            print(f"👤 {name} finalizou")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer_queue("Producer A", 2))
            tg.create_task(consumer_queue("Consumer A"))

        # Aguardar todas as tasks terminarem
        await queue.join()
        print(f"📊 Resultados: {results}")
        return results


async def demonstrate_locks():
    """Executa todos os exemplos de locks e sincronização."""
    print("🔒 DEMONSTRANDO LOCKS E SINCRONIZAÇÃO EM ASYNCIO...")
    print("=" * 60)

    # Executar todos os exemplos
    await AsyncLockExamples.basic_lock_example()
    await AsyncLockExamples.rlock_example()
    await AsyncLockExamples.semaphore_example()
    await AsyncLockExamples.event_example()
    await AsyncLockExamples.condition_example()
    await AsyncLockExamples.barrier_example()
    await AsyncLockExamples.queue_example()

    print("=" * 60)
    print("✅ Todos os exemplos de locks concluídos!")


if __name__ == "__main__":
    # Executar demonstração dos TaskGroups
    print("🎯 EXECUTANDO EXEMPLOS DE TASK GROUPS...")
    asyncio.run(task_groups())

    print("\n" + "=" * 60 + "\n")

    # Executar demonstração dos Futures
    print("🎯 EXECUTANDO EXEMPLOS DE FUTURES...")
    asyncio.run(main_future())

    print("\n" + "=" * 60 + "\n")

    # Executar demonstração dos Locks
    print("🎯 EXECUTANDO EXEMPLOS DE LOCKS...")
    asyncio.run(demonstrate_locks())
